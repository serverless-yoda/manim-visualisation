from manim import *
import pandas as pd
import numpy as np
import os

# ==============================================================
# CONFIGURATION
PLATFORM = 'yt_normal' # Options: 'tiktok', 'yt_short', 'yt_normal'
CHANNEL_NAME = "@YourHandle"
# ==============================================================

if PLATFORM in ['tiktok', 'yt_short']:
    config.pixel_height, config.pixel_width = 1920, 1080
    config.frame_height, config.frame_width = 16.0, 9.0
    IS_VERTICAL = True
else:
    config.pixel_height, config.pixel_width = 1080, 1920
    config.frame_height, config.frame_width = 8.0, 14.22
    IS_VERTICAL = False

class FinalFlagRace(Scene):
    DATA_PATH = "datasets/battle_tanks.csv"
    IMAGE_DIR = "images"
    TITLE_TEXT = "TANK PRODUCTION RACE"
    RUN_TIME = 30

    def setup_layout(self):
        if PLATFORM == 'tiktok':
            self.top_n, self.bar_h, self.spacing = 10, 0.5, 1.25
            self.font_sz = 24 
            self.left_anchor = LEFT * 3.8
            self.y_start = 5.5
        elif PLATFORM == 'yt_short':
            self.top_n, self.bar_h, self.spacing = 12, 0.45, 1.0
            self.font_sz = 22
            self.left_anchor = LEFT * 4.0
            self.y_start = 6.0
        else:
            self.top_n, self.bar_h, self.spacing = 12, 0.35, 0.55
            self.font_sz = 18
            self.left_anchor = LEFT * 6.2
            self.y_start = 3.2
        
        self.watermark_pos = DOWN * (config.frame_height/2 - 0.8)

    def construct(self):
        self.setup_layout()
        self.camera.background_color = "#050505"
        
        # 1. DATA PREP
        if not os.path.exists(self.DATA_PATH):
            print(f"Error: {self.DATA_PATH} not found.")
            return

        df = pd.read_csv(self.DATA_PATH, index_col=0).select_dtypes(include=[np.number]).interpolate().fillna(0)
        total_frames = self.RUN_TIME * 60
        df_expanded = df.reindex(np.linspace(df.index.min(), df.index.max(), total_frames)).interpolate()
        frame_tracker = ValueTracker(0)

        # 2. STATIC UI
        title = Text(self.TITLE_TEXT, font_size=35, weight=BOLD, color=BLUE_B).to_edge(UP, buff=0.5)
        watermark = Text(CHANNEL_NAME, font_size=20, color=WHITE).set_opacity(0.4).move_to(self.watermark_pos)
        
        year_bg = Integer(int(df.index[0]), group_with_commas=False).set_opacity(0.08).scale(3.5).move_to(ORIGIN)
        year_bg.add_updater(lambda m: m.set_value(int(df_expanded.index[int(min(frame_tracker.get_value(), total_frames-1))])))
        
        self.add(year_bg, title, watermark)

        # 3. COMPONENT REGISTRY
        bars, labels, values, flags = {}, {}, {}, {}

        for i, name in enumerate(df.columns):
            color = [BLUE_C, RED_C, GREEN_C, ORANGE, PURPLE_C, GOLD, PINK, TEAL][i % 8]
            
            bars[name] = Rectangle(width=0.1, height=self.bar_h, fill_opacity=0.9, stroke_width=0).set_fill(color).align_to(self.left_anchor, LEFT)
            labels[name] = Text(name, font_size=self.font_sz, weight=BOLD)
            values[name] = Integer(0, font_size=self.font_sz, group_with_commas=True)
            
            f_path = os.path.join(self.IMAGE_DIR, f"{name}.png")
            if os.path.exists(f_path):
                # Removed the RESAMPLING_ALGORITHM line to fix the NameError
                flags[name] = ImageMobject(f_path).scale_to_fit_height(self.bar_h * 0.8)
            else:
                flags[name] = Dot(radius=0).set_opacity(0)

        # 4. UPDATER
        def update_frame(mobj):
            f_idx = int(min(frame_tracker.get_value(), total_frames-1))
            row = df_expanded.iloc[f_idx].sort_values(ascending=False).head(self.top_n)
            current_max = row.iloc[0] if row.iloc[0] > 0 else 1

            for rank, (name, val) in enumerate(row.items()):
                r, l, v, f = bars[name], labels[name], values[name], flags[name]
                
                if val > 0:
                    if r not in self.mobjects: self.add(r, l, v, f)
                    
                    target_w = (val / current_max) * (config.frame_width * 0.7)
                    target_y = self.y_start - (rank * self.spacing)
                    
                    r.set_y(r.get_y() + (target_y - r.get_y()) * 0.2)
                    r.stretch_to_fit_width(max(target_w, 0.01), about_edge=LEFT).align_to(self.left_anchor, LEFT)
                    
                    if IS_VERTICAL:
                        l.move_to(r.get_left() + UP * (self.bar_h/2 + 0.25), aligned_edge=LEFT)
                    else:
                        l.next_to(r, LEFT, buff=0.2)
                    
                    v.set_value(int(val)).next_to(r, RIGHT, buff=0.2)
                    f.move_to(r.get_left() + RIGHT * (self.bar_h * 0.6))
                    
                    if rank == 0: r.set_stroke(WHITE, width=2, opacity=0.8)
                    else: r.set_stroke(width=0)
                else:
                    if r in self.mobjects: self.remove(r, l, v, f)

        self.add_updater(update_frame)

        # 5. RUN
        self.play(frame_tracker.animate.set_value(total_frames - 1), run_time=self.RUN_TIME, rate_func=linear)
        self.wait(3)
