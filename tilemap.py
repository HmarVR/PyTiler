import numpy as np
from model import NBaseVBO
import glm

class Tilemap:
    def __init__(self, app,
                       tile_size = 16,
                       size = 1000):
        # Store app and modern_gl context
        self.app = app
        self.ctx : mgl.Context = app.ctx

        # Store tilemap dimensions and tile size
        self.size = size
        self.tile_size = tile_size

        # Store a dict of :
        # - Key : Index position
        # - Value : Dict of :
        #     - Tileset type
        #     - Tile variant
        #     - Index position
        # Store a numpy array containing index positions of the tiles
        self.tilemap = {}
        self.block_arr = np.zeros((self.size * self.size, 3), dtype = 'f4')

        # A list containing offgrid items
        self.offgrid_items = []

        # Set default tiles for debug
        self.set_default_tiles()

        # Declare a buffer
        self.buffer = self.ctx.buffer(self.block_arr)

        self.vao = app.mesh.vao.get_ins_vao(app.mesh.vao.program.programs['tilemap'], 
                                            app.mesh.vao.vbo.vbos['cube'], 
                                            NBaseVBO(self.ctx, self.buffer))
        app.mesh.vao.vaos['tiles'] = self.vao
        
        self.tile_textures_array = app.mesh.texture.textures['grass_tileset']

        # Declare position, roll and scale
        self.pos = glm.vec3(0)
        self.roll = 0
        self.scale = glm.vec2(16)

        # Declare model matrix from pos, roll and scale
        self.m_model = self.get_model_matrix()
        
        # Declare program and camera
        self.program = self.vao.program
        self.camera = self.app.camera

    def set_default_tiles(self):
        # Iterate through the all of the tilemap
        for i in range(self.size):
            for j in range(self.size):
                # Set the tile at target index position to grass tile variant of 1
                self.tilemap[(j - self.size / 2, i - self.size / 2)] = {
                    'type': 'grass',
                    'variant': 1,
                    'position': (j - self.size / 2, i - self.size / 2)
                }

                self.block_arr[j + i * self.size] = [
                    j - self.size / 2,
                    i - self.size / 2,
                    0
                ]
                
        # Shapes the array into lists of lists of 3
        self.block_arr.reshape((self.size * self.size, 3))
        
        print(self.block_arr)

    def update(self):
        # Set parameters for the vert shader
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)

        # Bind texture array to slot 0
        # Bind the program texture array parameter to slot 0
        self.tile_textures_array.use(location = 0)
        self.program['Tiler'] = 0

    def get_model_matrix(self):
        m_model = glm.mat4()
        
        # Translate
        m_model = glm.translate(m_model, self.pos)
        # Rotate
        m_model = glm.rotate(m_model, glm.radians(self.roll), glm.vec3(0, 0, 1))
        # Scale
        m_model = glm.scale(m_model, glm.vec3(self.scale, 0))
        
        return m_model

    def render(self):
        # Reset model matrix base on position, roll and scale
        # Update parameters for the vert shader
        self.m_model = self.get_model_matrix()
        self.update()

        # Render using the VAO
        self.vao.render(instances = self.size * self.size)
