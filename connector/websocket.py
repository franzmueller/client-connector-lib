if __name__ == '__main__':
    exit('Please use "client.py"')

try:
    import websockets
    from modules.logger import root_logger
except ImportError as ex:
    exit("{} - {}".format(__name__, ex.msg))
import asyncio
import concurrent.futures
import functools
from queue import Queue, Empty
from threading import Thread

logger = root_logger.getChild(__name__)


class Websocket(Thread):
    def __init__(self, in_queue, out_queue, host, port):
        super().__init__()
        self._in_queue = in_queue
        self._out_queue = out_queue
        self._host = host
        self._port = port
        self._function_queue = Queue(1)
        self._stop_async = False
        self._websocket = None


    def _functionQueuePut(self, function, *args, **kwargs):
        self._function_queue.put((function, args, kwargs))


    def _retrieveAsyncResult(self, task):
        if task.exception():
            task.cancel()
        else:
            task.result()
        logger.debug("{}".format(task))


    @asyncio.coroutine
    def _spawnAsync(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            while not self._stop_async:
                try:
                    function, args, kwargs = yield from self._event_loop.run_in_executor(
                        executor,
                        functools.partial(self._function_queue.get, timeout=1)
                    )
                    self._event_loop.create_task(function(*args, **kwargs))
                except Empty:
                    pass
        logger.debug("spawn_async exited")


    def run(self):
        try:
            self._event_loop = asyncio.get_event_loop()
        except AssertionError:
            logger.debug("no event loop found")
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
            logger.debug("created new event loop")
        self._event_loop.run_until_complete(self._spawnAsync())
        self._event_loop.stop()
        self._event_loop.close()


    @asyncio.coroutine
    def _connect(self, callback):
        asyncio.Task.current_task().add_done_callback(self._retrieveAsyncResult)
        try:
            self._websocket = yield from websockets.connect(
                'ws://{}:{}'.format(self._host, self._port),
                loop=self._event_loop
            )
            logger.info("connected to '{}' on '{}'".format(self._host, self._port))
            #self._event_loop.call_soon_threadsafe(functools.partial(callback, True))
            callback(True)
        except OSError:
            logger.error("could not connect to '{}' on '{}'".format(self._host, self._port))
            #self._event_loop.call_soon_threadsafe(functools.partial(callback, False))
            callback(False)

    def connect(self, callback):
        self._functionQueuePut(self._connect, callback)
        self.start()


    @asyncio.coroutine
    def _shutdown(self, callback=None):
        asyncio.Task.current_task().add_done_callback(self._retrieveAsyncResult)
        logger.debug("stopping async tasks")
        self._stop_async = True
        try:
            yield from self._websocket.close()
            logger.info("connection closed")
        except:
            pass
        if callback:
            #self._event_loop.call_soon_threadsafe(callback)
            callback()

    def shutdown(self, callback):
        self._functionQueuePut(self._shutdown, callback)


    @asyncio.coroutine
    def _send(self, callback, payload):
        asyncio.Task.current_task().add_done_callback(self._retrieveAsyncResult)
        try:
            yield from self._websocket.send(payload)
            #self._event_loop.call_soon_threadsafe(functools.partial(callback, True))
            callback(True)
        except (websockets.WebSocketProtocolError, websockets.ConnectionClosed, BrokenPipeError):
            logger.warning("could not send data")
            #self._event_loop.call_soon_threadsafe(functools.partial(callback, False))
            callback(False)

    def send(self, payload, callback):
        self._functionQueuePut(self._send, payload, callback)


    @asyncio.coroutine
    def _receive(self, callback):
        asyncio.Task.current_task().add_done_callback(self._retrieveAsyncResult)
        try:
            payload = yield from self._websocket.recv()
            #self._event_loop.call_soon_threadsafe(functools.partial(callback, payload))
            callback(payload)
        except websockets.ConnectionClosed:
            #self._event_loop.call_soon_threadsafe(functools.partial(callback, False))
            callback(False)

    def receive(self, callback):
        self._functionQueuePut(self._receive, callback)


    @asyncio.coroutine
    def _ioRecv(self):
        #asyncio.Task.current_task().add_done_callback(self._retrieve_async_result)
        logger.debug("io receive task started")
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            while not self._stop_async:
                try:
                    payload = yield from self._websocket.recv()
                    yield from self._event_loop.run_in_executor(executor, self._in_queue.put, payload)
                except websockets.ConnectionClosed:
                    break

    @asyncio.coroutine
    def _ioSend(self):
        #asyncio.Task.current_task().add_done_callback(self._retrieve_async_result)
        logger.debug("io send task started")
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            while not self._stop_async:
                try:
                    payload = yield from self._event_loop.run_in_executor(
                        executor,
                        functools.partial(self._out_queue.get, timeout=1)
                    )
                    try:
                        yield from self._websocket.send(payload)
                    except (websockets.WebSocketProtocolError, websockets.ConnectionClosed, BrokenPipeError):
                        logger.warning("could not send data")
                        break
                except Empty:
                    pass

    @asyncio.coroutine
    def _ioStart(self, callback):
        asyncio.Task.current_task().add_done_callback(self._retrieveAsyncResult)
        logger.info("starting io operation")
        recv_task = self._event_loop.create_task(self._ioRecv())
        send_task = self._event_loop.create_task(self._ioSend())
        yield from asyncio.sleep(0.5)
        #self._event_loop.call_soon_threadsafe(callback)
        callback()
        done, pending = yield from asyncio.wait(
            (recv_task, send_task),
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
        yield from self._shutdown()
        logger.info("io operation stopped")

    def ioStart(self, callback):
        self._functionQueuePut(self._ioStart, callback)