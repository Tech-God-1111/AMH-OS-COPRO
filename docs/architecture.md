# AMH-OS architecture — early bring-up

## Processor roles
- **ESP32-S3 N16R8:** primary controller and future owner of the native UI/display stack.
- **ESP32-WROOM-32:** secondary controller for delegated I/O and future coprocessor services.

The boards are separate MCUs. They have independent CPUs, RAM and firmware images. UART is the current inter-processor transport; it does not create shared memory or a unified CPU.

## Current software state
This v0.1 bring-up establishes a newline-delimited JSON request/response protocol with identify, ping and status commands. There is no display driver, window manager, filesystem UI or desktop shell in this release.

## Planned layers
1. Hardware abstraction and board configuration.
2. Versioned inter-processor protocol.
3. Device and peripheral services.
4. Display driver and input stack after display hardware is selected.
5. Native shell / desktop environment.
