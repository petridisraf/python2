import pandas as pd
import matplotlib.pyplot as plt
import os

# Function to convert timecode to seconds
def timecode_to_seconds(tc):
    if pd.isnull(tc):
        return 0
    h, m, s, f = map(int, tc.split(':'))
    return h * 3600 + m * 60 + s + f / 30  # Assuming 30 fps

# Function to prepare the dataframe
def prepare_dataframe(csv_file):
    df = pd.read_csv(csv_file)
    df['Source In Sec'] = df['Source In'].apply(timecode_to_seconds)
    df['Source Out Sec'] = df['Source Out'].apply(timecode_to_seconds)
    df['Record Duration Sec'] = df['Record Duration'].apply(timecode_to_seconds)
    return df

# Load and prepare the first CSV file (sound tags)
csv_file1 = 'sound_1A.csv'  # Replace with your first CSV file path
df1 = prepare_dataframe(csv_file1)

# Load and prepare other CSV files (JRA video tags)
csv_files = [
    'JRA3-001-1A.csv', 'JRA3-002-1A.csv', 'JRA3-003-1A.csv', 
    'JRA3-004-1A.csv', 'JRA3-005-1A.csv', 'JRA3-006-1A.csv', 
    'JRA3-007-1A.csv', 'JRA3-008-1A.csv', 'JRA3-010-1A.csv',  
    'JRA3-011-1A.csv'  # Replace with your other CSV file paths
]

# Define individual tag colors directly
tag_colors = {
    'Στήλη': 'red',
    'Αέτωμα': 'green',
    'Πάνω δεξιά γωνία': 'purple',
    'Κάτω αριστερή γωνία': 'blue',
    'Γυναίκα αριστερά': 'yellow',
    'Γυναίκα όρθια': 'black',
    'Ενδιάμεσος άνδρας': 'brown',
    
    # Add more tags as needed
}

fig, ax = plt.subplots(figsize=(14, 8))

# Function to plot each dataframe
def plot_dataframe(ax, df, y_pos):
    for idx, row in df.iterrows():
        start_time = row['Source In Sec']
        end_time = row['Source Out Sec']
        duration = end_time - start_time
        tag = row['Notes']
        color = tag_colors.get(tag, 'gray')  # Default to gray if tag is not found
        rect = plt.Rectangle((start_time, y_pos - 0.1), duration, 0.2, color=color, alpha=0.5)
        ax.add_patch(rect)

# Plot the first dataframe (sound tags)
plot_dataframe(ax, df1, 1)

# Plot the other dataframes (JRA video tags)
for i, csv_file in enumerate(csv_files, start=2):
    df = prepare_dataframe(csv_file)
    plot_dataframe(ax, df, i)

# Set the y-ticks and labels with smaller font size
ax.set_yticks(list(range(1, len(csv_files) + 2)))
ax.set_yticklabels([os.path.splitext(os.path.basename(csv_file))[0] for csv_file in [csv_file1] + csv_files], fontsize=8)  # Smaller font size

# Labeling the timeline
ax.set_xlabel('Time (seconds)')
ax.set_ylabel('')

# Set limits and grid
ax.set_ylim(0.8, len(csv_files) + 1.2)
ax.grid(True, which='both', axis='x', linestyle='--', linewidth=0.5)

# Add legend in a separate window
legend_fig = plt.figure(figsize=(8, 6))
legend_handles = [plt.Line2D([0], [0], color=color, lw=4) for color in tag_colors.values()]
legend_labels = list(tag_colors.keys())
legend = legend_fig.legend(legend_handles, legend_labels, title="Tag Colors", loc='center')

ax.set_title('Video Clips Comparison Timeline')

plt.tight_layout()
plt.show()

# Function to compare tags between sound and JRA files based on tag colors
def compare_tags_by_color(df_sound, df_video):
    matches_by_color = {tag: [] for tag in tag_colors.keys()}
    for idx_sound, row_sound in df_sound.iterrows():
        sound_tag = row_sound['Notes']
        if sound_tag in tag_colors:
            for idx_video, row_video in df_video.iterrows():
                video_tag = row_video['Notes']
                if video_tag == sound_tag and not (
                    row_sound['Source Out Sec'] < row_video['Source In Sec'] or 
                    row_video['Source Out Sec'] < row_sound['Source In Sec']):
                    reaction_seconds = row_sound['Source In Sec'] - row_video['Source In Sec']
                    matches_by_color[sound_tag].append((row_sound, row_video, reaction_seconds))
    return matches_by_color

# Compare tags for each JRA file with the sound file and write to a text file
output_file = 'comparison_results_by_tag_color_1A.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    for csv_file in csv_files:
        df_video = prepare_dataframe(csv_file)
        matches_by_color = compare_tags_by_color(df1, df_video)
        f.write(f"Matches for {os.path.basename(csv_file)}:\n")
        for tag, matches in matches_by_color.items():
            if matches:
                f.write(f"\nTag: {tag}\n")
                for match in matches:
                    sound_tag = match[0]
                    video_tag = match[1]
                    reaction_seconds = match[2]
                    f.write(f"Sound Tag: {sound_tag['Notes']}, Time: {sound_tag['Source In']} - {sound_tag['Source Out']}\n")
                    f.write(f"Video Tag: {video_tag['Notes']}, Time: {video_tag['Source In']} - {video_tag['Source Out']}\n")
                    f.write(f"Reaction Seconds: {reaction_seconds:.2f}\n")
                    f.write("-" * 40 + "\n")
        f.write("=" * 80 + "\n\n")

print("Comparison results saved to", output_file)
