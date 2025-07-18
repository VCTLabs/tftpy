# vim: ts=4 sw=4 et ai:
"""This module implements the TFTP Client functionality. Instantiate an
instance of the client, and then use its upload or download method. Logging is
performed via a standard logging object set in TftpShared."""


import logging

from .TftpContexts import TftpContextClientDownload, TftpContextClientUpload
from .TftpPacketTypes import *
from .TftpShared import *

log = logging.getLogger("tftpy.TftpClient")


class TftpClient(TftpSession):
    """This class is an implementation of a tftp client. Once instantiated, a
    download can be initiated via the download() method, or an upload via the
    upload() method.

    The host and port options should be obvious. The options dict is tftp options.
    The localip is optional, but if provided, the client will bind to it for
    the transfer. The flock boolean is also optional, defaulting to True. If
    True, then any files read or written in the upload/download will be locked
    using advisory locking.
    """

    def __init__(self, host, port=69, options={}, localip="", flock=True):
        TftpSession.__init__(self)
        self.context = None
        self.host = host
        self.iport = port
        self.filename = None
        self.options = options
        self.localip = localip
        self.flock = flock
        if "blksize" in self.options:
            size = self.options["blksize"]
            tftpassert(isinstance(size, int), "blksize must be an int")
            if size < MIN_BLKSIZE or size > MAX_BLKSIZE:
                raise TftpException("Invalid blksize: %d" % size)

    def download(
        self,
        filename,
        output,
        packethook=None,
        timeout=SOCK_TIMEOUT,
        retries=DEF_TIMEOUT_RETRIES
    ):
        """This method initiates a tftp download from the configured remote
        host, requesting the filename passed. It writes the file to output,
        which can be a file-like object or a path to a local file. If a
        packethook is provided, it must be a function that takes a single
        parameter, which will be a copy of each DAT packet received in the
        form of a TftpPacketDAT object. The timeout parameter may be used to
        override the default SOCK_TIMEOUT setting, which is the amount of time
        that the client will wait for a receive packet to arrive.
        The retires parameter may be used to override the default DEF_TIMEOUT_RETRIES
        settings, which is the amount of retransmission attempts the client will initiate
        after encountering a timeout.

        Note: If output is a hyphen, stdout is used."""
        # We're downloading.
        log.debug("Creating download context with the following params:")
        log.debug(f"host = {self.host}, port = {self.iport}, filename = {filename}")
        log.debug("options = %s, packethook = %s, timeout = %s"
            % (self.options, packethook, timeout)
        )
        self.context = TftpContextClientDownload(
            self.host,
            self.iport,
            filename,
            output,
            self.options,
            packethook,
            timeout,
            retries=retries,
            localip=self.localip,
            flock=self.flock
        )
        with self.context as c:
            c.start()
            # Download happens here
            #self.context.end() - don't have to call end, it's called when we leave the context.

        metrics = self.context.metrics

        log.info("")
        log.info("Download complete.")
        if metrics.duration == 0:
            log.info("Duration too short, rate undetermined")
        else:
            log.info(
                "Downloaded %.2f bytes in %.2f seconds"
                % (metrics.bytes, metrics.duration)
            )
            log.info("Average rate: %.2f kbps" % metrics.kbps)
        log.info("%.2f bytes in resent data" % metrics.resent_bytes)
        log.info("Received %d duplicate packets" % metrics.dupcount)

    def upload(
        self,
        filename,
        input,
        packethook=None,
        timeout=SOCK_TIMEOUT,
        retries=DEF_TIMEOUT_RETRIES,
    ):
        """This method initiates a tftp upload to the configured remote host,
        uploading the filename passed. It reads the file from input, which
        can be a file-like object or a path to a local file. If a packethook
        is provided, it must be a function that takes a single parameter,
        which will be a copy of each DAT packet sent in the form of a
        TftpPacketDAT object. The timeout parameter may be used to override
        the default SOCK_TIMEOUT setting, which is the amount of time that
        the client will wait for a DAT packet to be ACKd by the server.
        The retires parameter may be used to override the default DEF_TIMEOUT_RETRIES
        settings, which is the amount of retransmission attempts the client will initiate
        after encountering a timeout.

        Note: If input is a hyphen, stdin is used."""
        self.context = TftpContextClientUpload(
            self.host,
            self.iport,
            filename,
            input,
            self.options,
            packethook,
            timeout,
            retries=retries,
            localip=self.localip,
            flock=self.flock
        )
        with self.context as c:
            c.start()
            # Upload happens here
            #self.context.end() - don't need to call this, done in context manager

        metrics = self.context.metrics

        log.info("")
        log.info("Upload complete.")
        if metrics.duration == 0:
            log.info("Duration too short, rate undetermined")
        else:
            log.info(
                "Uploaded %d bytes in %.2f seconds" % (
                    metrics.bytes, metrics.duration)
            )
            log.info("Average rate: %.2f kbps" % metrics.kbps)
        log.info("%.2f bytes in resent data" % metrics.resent_bytes)
        log.info("Resent %d packets" % metrics.dupcount)
