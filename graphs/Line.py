import sqlite3
import _Stage
class Stage(_Stage.Base):
	
	MENU_TITLE = 'Line Chart'
	ACTOR_TAG = 'line'
	
	def build(self):
		
		# Establish database connection
		dh = sqlite3.connect(self.master.db_path)
		cursor = dh.cursor()
		
		# Get range of data
		limits_sql = 'SELECT MIN(memory_usage), MAX(memory_usage), MIN(time_index), MAX(time_index) FROM trace'
		min_memory, max_memory, min_time, max_time = cursor.execute(limits_sql).fetchone()
		
		
		
		# Get range of window
		width, height = self.master.CANVAS.winfo_width() - 40, self.master.CANVAS.winfo_height() - 40
		top_offset = left_offset = 20
		
		sql = '''SELECT 
				a.level, a.function_number, a.memory_usage AS memory_start, b.memory_usage AS memory_end,
				a.time_index AS time_start, b.time_index AS time_end, a.user_defined
			FROM trace a JOIN trace b
				ON (a.level = b.level AND a.function_number = b.function_number AND b.entry = 1) 
			WHERE a.entry = 0
		'''
		_bprev = left_offset, height + top_offset
		for l,fn, ms, me, ts, te, ud in cursor.execute(sql):
			active_color = self.master.rc.get('primary_color' if ud > 0 else 'secondary_color')
			opts = {
				'capstyle' : 'round',
				'fill' : active_color,
				'width' : 6,
				'tags' : ('actor', self.ACTOR_TAG, self._create_tooltip_tag(l,fn), self._create_level_tag(l))
			}
			_bstart = int(ts / float(max_time) * width) + left_offset, height - int(ms / float(max_memory) * height) + top_offset
			_bend   = int(te / float(max_time) * width) + left_offset, height - int(me / float(max_memory) * height) + top_offset
			self.master.CANVAS.create_line(_bprev + _bstart,dash=(8,2,4,2,2,2),width=2,fill=self.master.rc.get('tertiary_color'), tags='actor')
			self.master.CANVAS.create_line(_bstart + _bend,**opts)
			_bprev = _bstart