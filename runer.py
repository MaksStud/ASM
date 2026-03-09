import logging

from unicorn import Uc, UC_ARCH_X86, UC_MODE_64, UC_HOOK_INSN
from unicorn.x86_const import UC_X86_REG_RSI, UC_X86_REG_RAX, UC_X86_REG_RDX, UC_X86_INS_SYSCALL, UC_X86_REG_RSP
from keystone import Ks, KS_ARCH_X86, KS_MODE_64


logger = logging.getLogger(__name__)


class RunAssembler:
    def __init__(self):
        logger.info("Initialization of the runner.")
        self.ks = Ks(KS_ARCH_X86, KS_MODE_64)
        self.BASE_ADDR = 0x1000000
        self.output = ""

    def syscall_hook(self, uc, user_data):
        logger.info("Using the syscall_hook method.")

        rax = uc.reg_read(UC_X86_REG_RAX)
        logger.debug(f"syscall rax={rax}")

        if rax == 1:
            rsi = uc.reg_read(UC_X86_REG_RSI)
            rdx = uc.reg_read(UC_X86_REG_RDX)
            logger.debug(f"write syscall: addr={hex(rsi)} size={rdx}")

            mem = uc.mem_read(rsi, rdx)
            decoded = mem.decode('utf-8', errors="ignore")
            logger.debug(f"Captured output chunk: {decoded!r}")

            self.output += decoded

        elif rax == 60:
            logger.info("Exit syscall received. Stopping emulation.")
            uc.emu_stop()

    def compile(self, asm_code: str):
        logger.info("Starting assembly compilation (no execution).")
        logger.debug(f"ASM code:\n{asm_code}")

        encoding, count = self.ks.asm(asm_code, self.BASE_ADDR)
        logger.debug(f"Assembly successful. Instructions count={count}")
        logger.info("Compilation finished successfully.")
        return bytes(encoding), count

    def run(self, asm_code: str):
        logger.info("Starting assembly execution.")
        logger.debug(f"ASM code:\n{asm_code}")

        try:
            self.output = ""

            encoding, count = self.ks.asm(asm_code, self.BASE_ADDR)
            logger.debug(f"Assembly successful. Instructions count={count}")

            machine_code = bytes(encoding)
            logger.debug(f"Machine code size={len(machine_code)} bytes")

            mu = Uc(UC_ARCH_X86, UC_MODE_64)
            logger.debug("Unicorn instance created.")

            mem_size = 2 * 1024 * 1024
            mu.mem_map(self.BASE_ADDR, mem_size)
            logger.debug(f"Memory mapped at {hex(self.BASE_ADDR)} size={mem_size}")

            mu.mem_write(self.BASE_ADDR, machine_code)
            logger.debug("Machine code written to memory.")

            stack_addr = self.BASE_ADDR + mem_size
            mu.reg_write(UC_X86_REG_RSP, stack_addr)
            logger.debug(f"Stack pointer set to {hex(stack_addr)}")

            mu.hook_add(
                UC_HOOK_INSN,
                self.syscall_hook,
                None,
                1,
                0,
                UC_X86_INS_SYSCALL
            )
            logger.debug("Syscall hook registered.")

            mu.emu_start(self.BASE_ADDR, self.BASE_ADDR + len(machine_code))
            logger.info("Execution finished successfully.")

            logger.debug(f"Final output: {self.output!r}")
            return self.output

        except Exception as e:
            logger.exception("Critical error during assembly execution.")
            return f"Critical error: {e}"
