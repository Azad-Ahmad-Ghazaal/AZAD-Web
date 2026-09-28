#include <efi.h>
#include <efilib.h>

EFI_STATUS EFIAPI efi_main(EFI_HANDLE ImageHandle, EFI_SYSTEM_TABLE *SystemTable) {
    InitializeLib(ImageHandle, SystemTable);
    ST->ConOut->ClearScreen(ST->ConOut);
    Print(L"MUAG OS v0.1\r\n");
    Print(L"================\r\n");
    Print(L"Boot successful: x86_64 UEFI\r\n");
    Print(L"Minimal recovery shell is alive.\r\n\r\n");
    Print(L"Press any key to power off.\r\n");
    UINTN Index; EFI_INPUT_KEY Key;
    ST->ConIn->Reset(ST->ConIn, FALSE);
    while (ST->ConIn->ReadKeyStroke(ST->ConIn, &Key) != EFI_SUCCESS)
        SystemTable->BootServices->WaitForEvent(1, &ST->ConIn->WaitForKey, &Index);
    ST->RuntimeServices->ResetSystem(EfiResetShutdown, EFI_SUCCESS, 0, NULL);
    return EFI_SUCCESS;
}
