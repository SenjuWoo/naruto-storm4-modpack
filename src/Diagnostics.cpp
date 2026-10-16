// Read-only native loader proof. It checks known beta guards without patching the game.
// WOO_STORM4_DEBUG=1 writes a bounded report under LocalAppData/SenjuWoo/Storm4Overhaul/logs.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <wincrypt.h>
#include <cstdio>
#include <cstring>
#include <cwchar>
#include "probes.h"

static constexpr const char* VERSION = "0.1.0";

// Refuse out-of-image reads even when loaded by an unrelated test executable.
static int Check(const unsigned char* image, SIZE_T imageSize, const Probe& probe, DWORD& error) {
    unsigned char actual[2048]{};
    SIZE_T read{};
    if (probe.rva > imageSize || probe.length > imageSize - probe.rva || probe.length > sizeof(actual)) return 2;
    if (!ReadProcessMemory(GetCurrentProcess(), image + probe.rva, actual, probe.length, &read)) {
        error = GetLastError(); return -1;
    }
    if (read != probe.length) { error = ERROR_PARTIAL_COPY; return -1; }
    unsigned char digest[32]{};
    DWORD digestSize = sizeof(digest);
    if (!CryptHashCertificate2(L"SHA256", 0, nullptr, actual, static_cast<DWORD>(probe.length), digest, &digestSize)) {
        error = GetLastError(); return -1;
    }
    return digestSize == sizeof(digest) && std::memcmp(digest, probe.digest, sizeof(digest)) == 0 ? 1 : 0;
}

// Use the documented API worker callback; its cadence is not a simulation tick.
extern "C" __declspec(dllexport) void __stdcall GameLoop(long long) {
    static LONG reported = 0;
    if (InterlockedCompareExchange(&reported, 1, 0) != 0) return;
    char enabled[8]{};
    if (GetEnvironmentVariableA("WOO_STORM4_DEBUG", enabled, sizeof(enabled)) != 1 || enabled[0] != '1') return;

    auto* image = reinterpret_cast<const unsigned char*>(GetModuleHandleW(nullptr));
    const auto* dos = reinterpret_cast<const IMAGE_DOS_HEADER*>(image);
    if (!image || dos->e_magic != IMAGE_DOS_SIGNATURE || dos->e_lfanew < 0 || dos->e_lfanew > 4096) return;
    const auto* nt = reinterpret_cast<const IMAGE_NT_HEADERS64*>(image + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE || nt->FileHeader.Machine != IMAGE_FILE_MACHINE_AMD64 ||
        nt->OptionalHeader.Magic != IMAGE_NT_OPTIONAL_HDR64_MAGIC) return;

    // Keep the last report only: no unbounded per-frame logging or personal identifiers.
    wchar_t root[MAX_PATH]{};
    DWORD length = GetEnvironmentVariableW(L"LOCALAPPDATA", root, MAX_PATH);
    if (!length || length >= MAX_PATH - 70) { OutputDebugStringA("Storm4 diagnostics: LOCALAPPDATA missing or too long\n"); return; }
    wchar_t folder[MAX_PATH]{};
    std::swprintf(folder, MAX_PATH, L"%ls\\SenjuWoo", root); CreateDirectoryW(folder, nullptr);
    std::swprintf(folder, MAX_PATH, L"%ls\\SenjuWoo\\Storm4Overhaul", root); CreateDirectoryW(folder, nullptr);
    std::swprintf(folder, MAX_PATH, L"%ls\\SenjuWoo\\Storm4Overhaul\\logs", root); CreateDirectoryW(folder, nullptr);
    wchar_t path[MAX_PATH]{};
    std::swprintf(path, MAX_PATH, L"%ls\\native-diagnostics.json", folder);
    HANDLE file = CreateFileW(path, GENERIC_WRITE, FILE_SHARE_READ, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (file == INVALID_HANDLE_VALUE) { OutputDebugStringA("Storm4 diagnostics: cannot create report\n"); return; }

    int counts[2]{};
    int readable[2]{}, outside[2]{}, failures[2]{};
    DWORD firstError{};
    for (int profile = 0; profile < 2; ++profile)
        for (int index = 0; index < 11; ++index) {
            DWORD error{};
            int result = Check(image, nt->OptionalHeader.SizeOfImage, PROFILES[profile][index], error);
            if (result == 2) ++outside[profile];
            else if (result < 0) { ++failures[profile]; if (!firstError) firstError = error; }
            else { ++readable[profile]; if (result == 1) ++counts[profile]; }
        }
    char report[1024]{};
    int bytes = std::snprintf(report, sizeof(report),
        "{\"version\":\"%s\",\"debug\":true,\"read_only\":true,\"pid\":%lu,"
        "\"image_size\":%lu,\"profile_matches\":[%d,%d],\"required_per_profile\":11,"
        "\"profile_readable\":[%d,%d],\"profile_out_of_bounds\":[%d,%d],"
        "\"profile_probe_failures\":[%d,%d],\"first_probe_error\":%lu,"
        "\"core_profile_candidate\":%s,\"native120_module_loaded\":%s,"
        "\"gameplay_validated\":false,\"callback\":\"API worker; not simulation tick\"}\n",
        VERSION, GetCurrentProcessId(), nt->OptionalHeader.SizeOfImage, counts[0], counts[1],
        readable[0], readable[1], outside[0], outside[1], failures[0], failures[1], firstError,
        counts[0] == 11 || counts[1] == 11 ? "true" : "false",
        GetModuleHandleW(L"Native120.dll") ? "true" : "false");
    DWORD written{};
    if (bytes <= 0 || bytes >= static_cast<int>(sizeof(report)) ||
        !WriteFile(file, report, static_cast<DWORD>(bytes), &written, nullptr) || written != static_cast<DWORD>(bytes))
        OutputDebugStringA("Storm4 diagnostics: report write failed\n");
    CloseHandle(file);
}

// No initialization hooks, memory writes, timers, or third-party callback ABI objects.
BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID) {
    if (reason == DLL_PROCESS_ATTACH) DisableThreadLibraryCalls(instance);
    return TRUE;
}
