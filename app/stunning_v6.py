from manim import *
import pandas as pd
import numpy as np
import os

# ==============================================================
# CONFIGURATION
PLATFORM = 'yt_normal' 
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

class UltimateFlagRace(Scene):
    DATA_PATH = "datasets/battle_tanks.csv"
    IMAGE_DIR = "images"
    TITLE_TEXT = "TANK PRODUCTION RACE"
    RUN_TIME = 30

    def setup_layout(self):
        if PLATFORM == 'yt_normal':
            self.top_n, self.bar_h, self.spacing = 10, 0.4, 0.6
            self.left_anchor = LEFT * 6.2
            self.y_start = 2.8 
            self.font_sz = 18
            self.milestone_pos = RIGHT * 5.2 + DOWN * 2.5
        else:
            self.top_n, self.bar_h, self.spacing = 10, 0.5, 1.1
            self.left_anchor = LEFT * 3.8
            self.y_start = 5.5
            self.font_sz = 24
            self.milestone_pos = RIGHT * 2.0 + DOWN * 6.5
        
        self.watermark_pos = DOWN * (config.frame_height/2 - 0.5) + RIGHT * (config.frame_width/2 - 1.5)

    def construct(self):
        self.setup_layout()
        self.camera.background_color = "#050505"
        
        # 1. DATA PREP
        df = pd.read_csv(self.DATA_PATH, index_col=0)
        df_numeric = df.select_dtypes(include=[np.number]).interpolate().fillna(0)
        total_frames = self.RUN_TIME * 60
        df_expanded = df_numeric.reindex(np.linspace(df_numeric.index.min(), df_numeric.index.max(), total_frames)).interpolate()
        frame_tracker = ValueTracker(0)

        # 2. UI ELEMENTS
        title = Text(self.TITLE_TEXT, font_size=35, weight=BOLD, color=BLUE_B).to_edge(UP, buff=0.3)
        watermark = Text(CHANNEL_NAME, font_size=18, color=WHITE).set_opacity(0.3).move_to(self.watermark_pos)

        # Milestone Dashboard
        self.year_txt = Integer(int(df_numeric.index[0]), group_with_commas=False).scale(1.2)
        self.total_val = Integer(0, group_with_commas=True).scale(1.0).set_color(GRAY_B)
        self.event_txt = Text("Starting...", font_size=18, color=BLUE_B, slant=ITALIC)

        milestone_box = VGroup(
            VGroup(Text("YEAR", font_size=12), self.year_txt).arrange(DOWN, buff=0.1),
            VGroup(Text("TOTAL PRODUCTION", font_size=12), self.total_val).arrange(DOWN, buff=0.1),
            VGroup(Text("EVENT", font_size=12), self.event_txt).arrange(DOWN, buff=0.1)
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT).move_to(self.milestone_pos).set_z_index(100)
        
        self.add(title, watermark, milestone_box)

        # 3. COMPONENT REGISTRY
        bars, labels, values, flags = {}, {}, {}, {}
        for i, name in enumerate(df_numeric.columns):
            color = [BLUE_C, RED_C, GREEN_C, ORANGE, PURPLE_C, GOLD, PINK, TEAL][i % 8]
            bars[name] = Rectangle(width=0.1, height=self.bar_h, fill_opacity=0.9, stroke_width=0).set_fill(color).align_to(self.left_anchor, LEFT)
            labels[name] = Text(name, font_size=self.font_sz, weight=BOLD)
            values[name] = Integer(0, font_size=self.font_sz, group_with_commas=True)
            
            f_path = os.path.join(self.IMAGE_DIR, f"{name}.png")
            flags[name] = ImageMobject(f_path).scale_to_fit_height(self.bar_h * 1.1) if os.path.exists(f_path) else Dot(radius=0).set_opacity(0)

        self.previous_ranks = {}

        # 4. UPDATER ENGINE
        def update_frame(mobj):
            f_idx = int(min(frame_tracker.get_value(), total_frames-1))
            current_year_val = df_expanded.index[f_idx]
            
            # Milestone Updates
            self.year_txt.set_value(int(current_year_val))
            self.total_val.set_value(int(df_expanded.iloc[f_idx].sum()))
            
            orig_years = df.index.values
            closest_year = orig_years[orig_years <= current_year_val][-1]
            current_event_str = str(df.loc[closest_year, "Milestone"])
            
            if self.event_txt.text != current_event_str:
                self.event_txt.become(
                    Text(current_event_str, font_size=18, color=BLUE_B, slant=ITALIC)
                    .next_to(milestone_box[2][0], DOWN, buff=0.1, aligned_edge=LEFT)
                )

            # Ranking Logic
            row = df_expanded.iloc[f_idx].sort_values(ascending=False).head(self.top_n)
            current_max = row.iloc[0] if row.iloc[0] > 0 else 1
            active_names = row.index.tolist()

            for rank, (name, val) in enumerate(row.items()):
                r, l, v, f = bars[name], labels[name], values[name], flags[name]
                if val > 0:
                    if r not in self.mobjects: self.add(r, l, v, f)
                    
                    target_w = (val / current_max) * (config.frame_width * 0.6)
                    target_y = self.y_start - (rank * self.spacing)
                    
                    # SWAP PHYSICS: 0.5 lerp for extreme snappiness
                    r.set_y(r.get_y() + (target_y - r.get_y()) * 0.5)
                    r.stretch_to_fit_width(max(target_w, 0.01), about_edge=LEFT).align_to(self.left_anchor, LEFT)
                    
                    if IS_VERTICAL:
                        l.move_to(r.get_left() + UP * (self.bar_h/2 + 0.2), aligned_edge=LEFT)
                    else:
                        l.next_to(r, LEFT, buff=0.15)
                    
                    v.set_value(int(val)).next_to(r, RIGHT, buff=0.2)
                    
                    # FLAGS ON FAR RIGHT: Anchor to the right edge of the bar
                    # We add a small offset so the flag is "leading" the bar
                    f.move_to(r.get_right() + RIGHT * 0.3)
                    
                    # SWAP FEEDBACK
                    if name in self.previous_ranks and self.previous_ranks[name] != rank:
                        r.set_stroke(WHITE, width=4, opacity=1)
                    else:
                        r.set_stroke(WHITE, width=2 if rank == 0 else 0, opacity=0.4)

            self.previous_ranks = {name: rnk for rnk, name in enumerate(active_names)}
            for n in bars:
                if n not in active_names and bars[n] in self.mobjects:
                    self.remove(bars[n], labels[n], values[n], flags[n])

        self.add_updater(update_frame)

        # 5. EXECUTION
        self.play(frame_tracker.animate.set_value(total_frames - 1), run_time=self.RUN_TIME, rate_func=linear)
        self.wait(2)