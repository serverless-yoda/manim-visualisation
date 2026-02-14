from manim import *
import pandas as pd
import numpy as np
import os
import random

class UltimateUniversalRace(MovingCameraScene):
    # SETTINGS
    DATA_PATH = "data/data.csv"
    TITLE = "Defense Spending $B by Country" # Change this to match your CSV row
    IMAGE_DIR = "images"
    WATERMARK_TEXT = "@YourChannelName"
    
    # Milestone dictionary: Add years and facts here
    MILESTONES = {
        1945: "End of WWII - Nuclear Age Begins",
        1960: "Cold War Defense Spending Spikes",
        1991: "Dissolution of the Soviet Union",
        2022: "Global Military Budget Shift",
    }

    def construct(self):
        # 1. DATA LOADING & FILTERING
        if not os.path.exists(self.DATA_PATH): return
        raw_df = pd.read_csv(self.DATA_PATH, index_col=0)
        numeric_df = raw_df.select_dtypes(include=[np.number]).interpolate().ffill().bfill().fillna(0)
        
        # Unit Logic based on Title
        prefix = "$" if "$" in self.TITLE else ""
        suffix = "%" if "%" in self.TITLE else (" Years" if "Life Expectancy" in self.TITLE else "")
        
        self.frame_mult = 4 
        df_orig = numeric_df.reindex(np.linspace(numeric_df.index.min(), numeric_df.index.max(), len(numeric_df) * self.frame_mult)).interpolate()
        df_scaled = df_orig / 1e9 if "$" in self.TITLE else df_orig
        self.top_n = min(len(numeric_df.columns), 10)

        # 2. FORMATTER
        def format_val(val, is_axis=False):
            actual_val = val * 1e9 if (is_axis and "$" in self.TITLE) else val 
            if actual_val >= 1e12: return f"{prefix}{actual_val/1e12:.1f}T{suffix}"
            if actual_val >= 1e9:  return f"{prefix}{actual_val/1e9:.1f}B{suffix}"
            return f"{prefix}{actual_val:.1f}{suffix}"

        # 3. CHART SETUP
        init_data = df_scaled.iloc[0].sort_values(ascending=False).head(self.top_n)
        y_max_limit = df_scaled.values.max() * 1.1
        
        chart = BarChart(
            values=init_data.values.tolist(),
            y_range=[0, y_max_limit, y_max_limit / 5],
            x_length=10, y_length=5,
            y_axis_config={"include_numbers": False, "stroke_opacity": 0},
            x_axis_config={"stroke_opacity": 0},
        ).shift(DOWN*0.9)
        chart.y_axis.numbers.set_opacity(0) # Hide ghost numbers

        # 4. STATIC UI ELEMENTS (Watermark & Background)
        watermark = Text(self.WATERMARK_TEXT, font="Monospace", font_size=16, opacity=0.4).to_corner(DR)
        title_label = Text(self.TITLE, font_size=28, color=BLUE_A).to_edge(UP, buff=0.5)
        self.add(watermark, title_label)

        # 5. DYNAMIC UI ELEMENTS (Milestones & Year)
        year_tracker = ValueTracker(df_orig.index[0])
        
        year_display = always_redraw(lambda: 
            Text(str(int(year_tracker.get_value())), font="Monospace", font_size=48, opacity=0.8).to_corner(UR)
        )
        
        desc_box = always_redraw(lambda:
            Text(self.MILESTONES.get(int(year_tracker.get_value()), ""), font_size=18, color=GRAY_A)
            .next_to(chart, DOWN, buff=0.4)
        )

        # Milestone Line (A goal line that stays at a specific value, e.g., 500)
        goal_val = y_max_limit * 0.7 
        milestone_line = always_redraw(lambda:
            DashedLine(
                chart.y_axis.number_to_point(goal_val),
                chart.y_axis.number_to_point(goal_val) + RIGHT * 10,
                color=YELLOW, stroke_opacity=0.3
            )
        )

        # 6. ANIMATION LOOP SETUP
        y_label_group = VGroup()
        label_group = VGroup(*[VGroup() for _ in range(self.top_n)])
        
        # Load Flags
        country_assets = {}
        for country in numeric_df.columns:
            img_path = os.path.join(self.IMAGE_DIR, f"{country}.png")
            flag = ImageMobject(img_path).scale_to_fit_height(0.3) if os.path.exists(img_path) else Dot(radius=0).set_opacity(0)
            country_assets[country] = flag

        self.add(chart, y_label_group, year_display, desc_box, milestone_line, label_group)

        # 7. THE RACE
        previous_order = list(init_data.index)
        for i in range(1, len(df_scaled)):
            curr_scaled = df_scaled.iloc[i].sort_values(ascending=False).head(self.top_n)
            curr_orig = df_orig.iloc[i].sort_values(ascending=False).head(self.top_n)
            current_order = list(curr_scaled.index)
            
            # Clear Y-axis "ghosts"
            y_label_group.submobjects = [] 
            curr_max = curr_scaled.max() if curr_scaled.max() > 0 else 1
            for j in range(1, 6):
                val = (curr_max / 5) * j
                pos = chart.y_axis.number_to_point(val)
                lbl = Text(format_val(val, is_axis=True), font_size=16, color=WHITE, opacity=0.4)
                lbl.next_to(pos, LEFT, buff=0.4)
                y_label_group.add(lbl)

            active_flags = []
            for idx in range(self.top_n):
                name = current_order[idx]
                val_orig = curr_orig.iloc[idx]
                
                # Update Bars & Flags
                chart.bars[idx].set_fill(color=WHITE if idx==0 else BLUE_E, opacity=0.8)
                f = country_assets[name]
                f.move_to(chart.bars[idx].get_corner(UR) + RIGHT*0.25)
                active_flags.append(f)
                if f not in self.mobjects: self.add(f)

                # Update Labels
                lbl = Text(f"{name}: {format_val(val_orig)}", font="Monospace", font_size=12)
                lbl.add_background_rectangle(opacity=0.7, color=BLACK)
                label_group[idx].become(lbl.next_to(chart.bars[idx], UP, buff=0.15))

            self.play(
                chart.animate(run_time=0.04, rate_func=linear).change_bar_values(curr_scaled.values.tolist()),
                year_tracker.animate(run_time=0.04, rate_func=linear).set_value(df_orig.index[i]),
            )
            
            # Cleanup
            for country, f in country_assets.items():
                if f not in active_flags and f in self.mobjects: self.remove(f)

        self.wait(2)

# uv run manim -pqh --fps 60 stunning_v6.py UltimateUniversalRace