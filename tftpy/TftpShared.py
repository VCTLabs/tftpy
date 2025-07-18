# vim: ts=4 sw=4 et ai:
"""This module holds all objects shared by all other modules in tftpy."""

locking_method = None
try:
    import fcntl
    locking_method = 'fcntl'
except:
    try:
        import msvcrt
        locking_method = 'msvcrt'
        import os
    except:
        raise AssertionError("Unsupported locking method on platform")

MIN_BLKSIZE = 8
DEF_BLKSIZE = 512
MAX_BLKSIZE = 65536
SOCK_TIMEOUT = 5
MAX_DUPS = 20
DEF_TIMEOUT_RETRIES = 3
DEF_TFTP_PORT = 69

import logging

log = logging.getLogger("tftpy.TftpShared")

# A hook for deliberately introducing delay in testing.
DELAY_BLOCK = 0
# A hook to simulate a bad network
NETWORK_UNRELIABILITY = 0
# 0 is disabled, anything positive is the inverse of the percentage of
# dropped traffic. For example, 1000 would cause 0.1% of DAT packets to
# be skipped to simulate lost packets.

def lockfile(fobj, shared=True, blocking=True, unlock=False):
    """Take appropriate action to advisory lock the file with the descriptor provided,
    depending on the platform. fobj must be a file object."""
    log.debug("lockfile on %s, shared %s, blocking %s, unlock %s",
              fobj.name, shared, blocking, unlock)
    if locking_method == "fcntl":
        mode = fcntl.LOCK_UN if unlock else fcntl.LOCK_SH if shared else fcntl.LOCK_EX
        if not unlock and not blocking:
            mode |= fcntl.LOCK_NB
        fcntl.flock(fobj, mode)
    else:
        mode = msvcrt.LK_UNLCK if unlock else msvcrt.LK_RLCK if shared else msvcrt.LK_LOCK
        if not unlock and not blocking:
            mode = msvcrt.LK_NBLCK if not shared else msvcrt.LK_NBRLCK
        # Want to lock the whole file.
        pos = fobj.tell()
        log.debug("position is %s", pos)
        fobj.seek(0, os.SEEK_END)
        nbytes = fobj.tell()
        log.debug("nbytes is %s", nbytes)
        # Odd, I get permission denied on the unlock
        if unlock:
            return
        msvcrt.locking(fobj.fileno(), mode, nbytes)

def tftpassert(condition, msg):
    """This function is a simple utility that will check the condition
    passed for a false state. If it finds one, it throws a TftpException
    with the message passed. This just makes the code throughout cleaner
    by refactoring."""
    if not condition:
        raise TftpException(msg)


class TftpErrors:
    """This class is a convenience for defining the common tftp error codes,
    and making them more readable in the code."""

    NotDefined = 0
    FileNotFound = 1
    AccessViolation = 2
    DiskFull = 3
    IllegalTftpOp = 4
    UnknownTID = 5
    FileAlreadyExists = 6
    NoSuchUser = 7
    FailedNegotiation = 8


class TftpException(Exception):
    """This class is the parent class of all exceptions regarding the handling
    of the TFTP protocol."""

    pass


class TftpTimeout(TftpException):
    """This class represents a timeout error waiting for a response from the
    other end."""

    pass


class TftpTimeoutExpectACK(TftpTimeout):
    """This class represents a timeout error when waiting for ACK of the current block
    and receiving duplicate ACK for previous block from the other end."""

    pass


class TftpFileNotFoundError(TftpException):
    """This class represents an error condition where we received a file
    not found error."""

    pass
