from pyglet import gl
from ctypes import sizeof


class Buffer:

    def __init__(self):
        self.id = gl.GLuint(0)

    def get_id(self):
        return self.id


class FrameBuffer(Buffer):

    def __init__(self):
        Buffer.__init__(self)
        self.__create_buffer()

    def __create_buffer(self):
        # generate the frame buffer
        gl.glGenFramebuffers(1, self.id)
        # use frame buffer
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.id)

    def bind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.id)

    def unbind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.id)
