// theoutfit - ReXGlue Recompiled Project
//
// Customize your app by overriding virtual hooks from rex::ReXApp.

#pragma once

#include <atomic>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <thread>
#include <vector>

#include <rex/logging.h>
#include <rex/ppc/context.h>
#include <rex/rex_app.h>
#include <rex/system/thread_state.h>
#include <rex/system/xthread.h>

class TheoutfitApp : public rex::ReXApp {
 public:
  using rex::ReXApp::ReXApp;

  ~TheoutfitApp() override {
    StopMainThreadWatchdog();
  }

  static std::unique_ptr<rex::ui::WindowedApp> Create(
      rex::ui::WindowedAppContext& ctx) {
    return std::unique_ptr<TheoutfitApp>(new TheoutfitApp(ctx, "theoutfit",
        PPCImageConfig));
  }

  // Override virtual hooks for customization:
  // void OnPostInitLogging() override {}
  // void OnPreSetup(rex::RuntimeConfig& config) override {}
  // void OnLoadXexImage(std::string& xex_image) override {}
  // void OnPostSetup() override {}
  // void OnCreateDialogs(rex::ui::ImGuiDrawer* drawer) override {}
  void OnConfigurePaths(rex::PathConfig& paths) override {
    if (!paths.game_data_root.empty()) {
      return;
    }

    const auto exe_dir = paths.config_path.parent_path();
    for (const auto& candidate : GetGameDataRootCandidates(exe_dir)) {
      if (std::filesystem::is_regular_file(candidate / "default.xex")) {
        paths.game_data_root = candidate;
        return;
      }
    }
  }

  void OnShutdown() override {
    REXLOG_INFO("TheOutfit diag: shutdown requested");
    StopMainThreadWatchdog();
  }

  void OnPostLoadXexImage() override {
    REXLOG_INFO("TheOutfit diag: XEX image loaded");
  }

  void OnPreLaunchModule() override {
    REXLOG_INFO("TheOutfit diag: pre-launch module");
  }

  void OnPostLaunchModule(rex::system::XThread* thread) override {
    if (thread == nullptr) {
      REXLOG_INFO("TheOutfit diag: post-launch module thread=null");
      return;
    }

    const auto* params = thread->creation_params();
    REXLOG_INFO(
        "TheOutfit diag: post-launch module thread_id={} pcr={:08X} "
        "start={:08X} startup={:08X} context={:08X} stack_size={:08X} "
        "flags={:08X} process={:08X}",
        thread->thread_id(), thread->pcr_ptr(), params->start_address,
        params->xapi_thread_startup, params->start_context,
        params->stack_size, params->creation_flags, params->guest_process);
    StartMainThreadWatchdog(thread);
  }

  void OnGuestThreadExit(rex::system::XThread* thread) override {
    if (thread == nullptr) {
      REXLOG_INFO("TheOutfit diag: guest thread exit thread=null");
    } else {
      REXLOG_INFO("TheOutfit diag: guest thread exit thread_id={} running={}",
                  thread->thread_id(), thread->is_running());
    }
    StopMainThreadWatchdog();
  }

 private:
  static std::vector<std::filesystem::path> GetGameDataRootCandidates(
      std::filesystem::path root) {
    std::vector<std::filesystem::path> candidates;

    for (int depth = 0; depth < 6 && !root.empty(); ++depth) {
      candidates.push_back(root / "game_files");
      candidates.push_back(root / "assets" / "game_files");

      const auto parent = root.parent_path();
      if (parent == root) {
        break;
      }
      root = parent;
    }

    return candidates;
  }

  void StartMainThreadWatchdog(rex::system::XThread* thread) {
    StopMainThreadWatchdog();
    watchdog_running_.store(true);
    watchdog_thread_ = std::thread([this, thread]() {
      uint32_t previous_lr = 0;
      uint32_t previous_ctr = 0;
      uint32_t previous_indirect = 0;
      uint32_t steady_ticks = 0;

      for (uint32_t tick = 1; watchdog_running_.load(); ++tick) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        if (!watchdog_running_.load()) {
          break;
        }

        auto* thread_state = thread->thread_state();
        auto* ctx = thread_state != nullptr ? thread_state->context() : nullptr;
        if (ctx == nullptr) {
          REXLOG_INFO(
              "TheOutfit diag: main-thread watchdog tick={} thread_id={} "
              "running={} context=null",
              tick, thread->thread_id(), thread->is_running());
          continue;
        }

        const auto lr = static_cast<uint32_t>(ctx->lr);
        const auto ctr = static_cast<uint32_t>(ctx->ctr.u64);
        const auto indirect = ctx->last_indirect_target;
        const auto r24 = static_cast<uint32_t>(ctx->r24.u64);
        const auto r31 = static_cast<uint32_t>(ctx->r31.u64);
        if (tick > 1 && lr == previous_lr && ctr == previous_ctr &&
            indirect == previous_indirect) {
          ++steady_ticks;
        } else {
          steady_ticks = 0;
        }

        REXLOG_INFO(
            "TheOutfit diag: main-thread watchdog tick={} steady={} "
            "thread_id={} running={} lr={:08X} ctr={:08X} indirect={:08X} "
            "r1={:08X} r2={:08X} r3={:08X} r4={:08X} r5={:08X} "
            "r13={:08X} r20={:08X} r21={:08X} r24={:08X} r25={:08X} "
            "r26={:08X} r27={:08X} r29={:08X} r30={:08X} r31={:08X}",
            tick, steady_ticks, thread->thread_id(), thread->is_running(), lr,
            ctr, indirect, static_cast<uint32_t>(ctx->r1.u64),
            static_cast<uint32_t>(ctx->r2.u64),
            static_cast<uint32_t>(ctx->r3.u64),
            static_cast<uint32_t>(ctx->r4.u64),
            static_cast<uint32_t>(ctx->r5.u64),
            static_cast<uint32_t>(ctx->r13.u64),
            static_cast<uint32_t>(ctx->r20.u64),
            static_cast<uint32_t>(ctx->r21.u64), r24,
            static_cast<uint32_t>(ctx->r25.u64),
            static_cast<uint32_t>(ctx->r26.u64),
            static_cast<uint32_t>(ctx->r27.u64),
            static_cast<uint32_t>(ctx->r29.u64),
            static_cast<uint32_t>(ctx->r30.u64), r31);

        previous_lr = lr;
        previous_ctr = ctr;
        previous_indirect = indirect;
      }
    });
  }

  void StopMainThreadWatchdog() {
    const bool was_running = watchdog_running_.exchange(false);
    if (watchdog_thread_.joinable() &&
        watchdog_thread_.get_id() != std::this_thread::get_id()) {
      watchdog_thread_.join();
    }
    if (was_running) {
      REXLOG_INFO("TheOutfit diag: main-thread watchdog stopped");
    }
  }

  std::atomic<bool> watchdog_running_{false};
  std::thread watchdog_thread_;
};
