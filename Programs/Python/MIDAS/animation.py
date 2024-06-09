import re
from screeninfo import get_monitors

from MIDAS.enums import *

from Animation.Animation_2d import *
from Animation.Colormap import *

class Animation2d(Animation_2d):
    
  # ------------------------------------------------------------------------
  #   Constructor
  # ------------------------------------------------------------------------

  def __init__(self, engine):

    # Define engine
    self.engine = engine
    self.dim = self.engine.geom.dimension

    # Animation constructor
    super().__init__(self.engine.window,
                     boundaries=[np.array([-1, 1])*self.engine.geom.arena_shape[0]/2,
                                 np.array([-1, 1])*self.engine.geom.arena_shape[1]/2],
                    disp_boundaries=False)

    # Default display options
    self.options = {}
    for k in self.engine.agents.group_names:
      self.options[k] = {
        'color': 'white', 
        'cmap': None,
        'cmap_on': 'x0',
        'cmap_dynamic': None,
        'size': 0.01
      }

    # Trajectory trace
    self.trace_duration = None

  # ------------------------------------------------------------------------
  #   Initialization
  # ------------------------------------------------------------------------
   
  def initialize(self):

    # Define padding
    padding = np.max([self.options[k]['size'] for k in self.options])    
    self.setPadding(padding)

    # === Boundaries =======================================================

    thickness = int(get_monitors()[0].width/1920)

    match self.engine.geom.arena:

      case Arena.CIRCULAR:
        
        if self.engine.geom.periodic:
          self.add(circle, 'boundary', 
                   position = [0,0],
                   radius = self.engine.geom.arena_shape[0]/2,
                   colors = (None, 'grey'),
                   linestyle = '--',
                  thickness=thickness)
        else:
          self.add(circle, 'boundary', 
                   position = [0,0],
                   radius = self.engine.geom.arena_shape[0]/2,
                   colors = (None, 'white'),
                  thickness=thickness)

      case Arena.RECTANGULAR:
        
        pts_left = [[-self.engine.geom.arena_shape[0]/2, -self.engine.geom.arena_shape[1]/2],
                    [-self.engine.geom.arena_shape[0]/2, self.engine.geom.arena_shape[1]/2]]
        pts_right = [[self.engine.geom.arena_shape[0]/2, -self.engine.geom.arena_shape[1]/2],
                     [self.engine.geom.arena_shape[0]/2, self.engine.geom.arena_shape[1]/2]]
        pts_top = [[-self.engine.geom.arena_shape[0]/2, self.engine.geom.arena_shape[1]/2],
                    [self.engine.geom.arena_shape[0]/2, self.engine.geom.arena_shape[1]/2]]
        pts_bottom = [[-self.engine.geom.arena_shape[0]/2, -self.engine.geom.arena_shape[1]/2],
                    [self.engine.geom.arena_shape[0]/2, -self.engine.geom.arena_shape[1]/2]]

        # X-periodicity
        if self.engine.geom.periodic[0]:
          self.add(line, 'boundary_left', points = pts_left, color = 'grey', linestyle = '--', thickness=thickness)
          self.add(line, 'boundary_right', points = pts_right, color = 'grey', linestyle = '--', thickness=thickness)
        else:
          self.add(line, 'boundary_left', points = pts_left, color = 'white', thickness=thickness)
          self.add(line, 'boundary_right', points = pts_right, color = 'white', thickness=thickness)

        # X-periodicity
        if self.engine.geom.periodic[1]:
          self.add(line, 'boundary_top', points = pts_top, color = 'grey', linestyle = '--', thickness=thickness)
          self.add(line, 'boundary_bottom', points = pts_bottom, color = 'grey', linestyle = '--', thickness=thickness)
        else:
          self.add(line, 'boundary_top', points = pts_top, color = 'white', thickness=thickness)
          self.add(line, 'boundary_bottom', points = pts_bottom, color = 'white', thickness=thickness)

    # === Agents ===========================================================

    # Agent's triangle shape
    pts = np.array([[1,0],[-0.5,0.5],[-0.5,-0.5]])

    for i in range(self.engine.agents.N_agents):

      # Group options
      opt = self.options[self.engine.agents.group_names[self.engine.agents.group[i]]]

      # --- Color

      # Colormap and color
      if opt['cmap'] is None:
        color = opt['color']
      else:
        color = None
        cmap = Colormap(name=opt['cmap'])

      if color is None:
        match opt['cmap_on']:

          case 'index': # Color on index
            n = np.count_nonzero(self.engine.agents.group==self.engine.agents.group[i])
            cmap.range = [0, n-1]
            clrs = (cmap.qcolor(i), None)

          case 'x0': # Color on x-position (default)
            cmap.range = self.boundaries['x']
            clrs = (cmap.qcolor(self.engine.agents.pos[i,0]), None)

          case 'y0': # Color on y-position   
            cmap.range = self.boundaries['y']         
            clrs = (cmap.qcolor(self.engine.agents.pos[i,1]), None)

          case 'z0': # Color on z-position            
            cmap.range = self.boundaries['z']
            clrs = (cmap.qcolor(self.engine.agents.pos[i,2]), None)

      elif isinstance(color, tuple):
        clrs = color

      else:
        clrs = (color, None)

      # --- Shape

      if self.engine.agents.atype[i]==Agent.FIXED:
        '''
        Fixed agents
        '''

        self.add(circle, i,
          position = self.engine.agents.pos[i,:],
          radius = 0.005,
          colors = clrs,
          zvalue=-1
        )

      else:
        '''
        Moving agents
        '''

        self.add(polygon, i,
          position =  self.engine.agents.pos[i,:],
          orientation = self.engine.agents.vel[i,1],
          points = pts*opt['size'],
          colors = clrs,
        )

        # === Traces =======================================================
          
        # if self.trace_duration is not None:

        #   # Initialize trace coordinates
        #   Ag.trace = np.ones((self.trace_duration,1))*np.array([Ag.x, Ag.y])
      
        #   # Trace polygon
        #   self.add(path, f'{i:d}_trace',
        #     position = [0, 0],
        #     orientation = 0,
        #     points = Ag.trace,
        #     colors = (None, clrs[0]),
        #     thickness = 3
        #   )

  # ------------------------------------------------------------------------
  #   Informations
  # ------------------------------------------------------------------------
   
  def time_str(self):

    pass
    # s = '<p>step {:06d}</p>'.format(self.step)

    # # Grey zeros
    # s = re.sub(r'( )([0]+)', r'\1<span style="color:grey;">\2</span>', s)

    # print('ok')

    # # Agents that are not fixed
    # s += '<p>{:d} agents</p>'.format(np.count_nonzero(self.engine.agents.atype))

    # if not self.engine.periodic_boundary_condition:
    #   s += '<p style="font-size:20px;">Bouncing boundary condition</p>'

    # return s

  def add_info(self, agent=None):

    # Define agent
    if agent is None:
      agent = self.info_agent

    # Get information
    info = agent.information()

    self.engine.window.information.add(text, 'info',
      stack = True,
      string = info,
      color = 'white',
      fontsize = 10,
    )

    # match self.engine.animation.options[self.name]['dynamic_cmap']:
  
    #   case 'speed':
    #     self.engine.animation.colormap.range = [self.v_min, self.v_max]
    #     self.engine.animation.add_insight_colorbar()

    #   case 'density':
    #     self.engine.animation.colormap.range = [1, 20]
    #     self.engine.animation.add_insight_colorbar()

  def add_info_weights(self, agent=None):
    '''
    Information over weights displayed in a piechart style
    '''
    
    if agent is None:
      agent = self.info_agent

    agent.add_info_weights()
    agent.update_info_weights()

  def add_info_colorbar(self):

    pass
    # self.add(colorbar, 'Cb',
    #   insight = True,
    #   height = 'fill',
    #   nticks = 2
    # )

  # ------------------------------------------------------------------------
  #   Updates
  # ------------------------------------------------------------------------
   
  def update(self, t):
    
    # Update timer display
    super().update(t)

    # Compute step
    self.engine.step(t.step)

    # Update display
    self.update_display()

    # Update traces
    # if self.trace_duration is not None:
    #   for i, Ag in enumerate(self.engine.agents.list):
    #     Ag.trace = np.roll(Ag.trace, 1, axis=0)
    #     Ag.trace[0,0] = Ag.x
    #     Ag.trace[0,1] = Ag.y

    #     # Periodic boundary conditions
    #     Ag.trace = np.unwrap(Ag.trace, period=1, axis=0)
    #     Ag.trace[Ag.trace<0] = 0
    #     Ag.trace[Ag.trace>1] = 1
        
  def update_display(self):
    '''
    Update display
    '''
    
    for i in range(self.engine.agents.N_agents):

      # Skip fixed agents
      if self.engine.agents.atype[i]==0: continue

      # Position
      self.item[i].position = self.engine.agents.pos[i]

      # Orientation
      self.item[i].orientation = self.engine.agents.vel[i,1]

      # Color
      # match self.options[self.engine.agents.list[i].name]['cmap_dynamic']:
      #   case 'speed':
      #     self.item[i].colors = (self.colormap.qcolor(self.engine.agents.list[i].v), None)
      #   case 'density':
      #     if self.engine.agents.list[i].density is not None:
      #       self.item[i].colors = (self.colormap.qcolor(self.engine.agents.list[i].density), None)
      #   case 'custom':
      #     self.item[i].colors = (self.colormap.qcolor(self.engine.agents.list[i].get_color()), None)
    
      # Traces
      # if self.trace_duration is not None:
      #   self.item[f'{i:d}_trace'].points = Ag.trace