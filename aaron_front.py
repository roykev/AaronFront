import collections
import io

from st_click_detector import click_detector
import os
import streamlit as st
import pandas as pd
import tempfile


from utils.aa_utils import find_txt, get_audio_file_content, get_binary_file_downloader_html, range2start_end, set_svg_text_direction, aaFrontConfig

sections = ["Short_Summary", "MindMap", "Quiz", "Long_Summary", "Concepts", "Additional"]


# Function to extract tags from the audio file
def extract_tags():
    # Replace this with your logic to extract tags from the audio file
    # For demonstration purpose, returning dummy tags
    data = {}
    if st.session_state.concepts is not None:
        arr = st.session_state.concepts.split('\n')
        for row in arr:
            concept_vec = row.split(';')
            if len(concept_vec) == 2:
                term = concept_vec[0].strip()
                times_arr = concept_vec[1].strip().split(",")
                data[term] = times_arr
    else:


        # Data setup
        data = {"AAA": ["00:10-00:30", '01:11-02:30'],
                "BBB": ['02:11-03:00'],
                "Z": ['01:16-01:30']}

    return data



def load_files(cont):
    # Set up tkinter
  #  root = tk.Tk()
   # root.withdraw()
    # Make folder picker dialog appear on top of other windows
    #root.wm_attributes('-topmost', 1)

    # Folder picker button
    # cont.title('Folder Picker')
    col1, col2, = cont.columns(2)
    col2.image("media/aaron.jpg")
    audio_file = col1.file_uploader("Choose an audio file", type=['mp3', 'wav'])
    if audio_file is not None:
        st.session_state.audio_file = audio_file
        st.session_state.audio_bytes = audio_file.getvalue()
        st.session_state.audio_format = audio_file.type.split('/')[-1]
    uploaded_files = col1.file_uploader("Choose the AI outputs", accept_multiple_files=True)
    for u_file in uploaded_files:
        if 'text' in u_file.type:
            text_content = u_file.getvalue().decode('utf-8')
            if "additional" in u_file.name.lower():
                st.session_state["additional"] = text_content
            if "short_summary" in u_file.name.lower():
                st.session_state["short_summary"] = text_content
            if "long_summary" in u_file.name.lower():
                st.session_state["long_summary"] = text_content
            if "quiz" in u_file.name.lower():
                st.session_state["quiz"] = text_content
            if "concepts" in u_file.name.lower():
                st.session_state["concepts"] = text_content
        elif 'svg' in u_file.type:
            # Read the SVG file content
            svg_content = u_file.read().decode("utf-8")
            # Modify the SVG for RTL text direction
            svg_content_rtl = set_svg_text_direction(svg_content)
            st.session_state['mindmap']=svg_content_rtl






# Function to render the HTML audio player with start and end times
def audio_player(file_path, start_time, end_time):
    # HTML template for the audio player with JavaScript to set and monitor times
    file_path = "media/audio.mp3"
    audio_data_url = get_audio_file_content(file_path)

    audio_html = f"""
    <audio id="audioPlayer" controls>
       <source src="data:audio/mp3;base64,{audio_data_url}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    <script>
        document.addEventListener('DOMContentLoaded', (event) => {{
            const audioPlayer = document.getElementById('audioPlayer');
            // Set the start time in seconds
            audioPlayer.currentTime = {start_time};
            // Play the audio
            audioPlayer.play();
            // Function to stop audio at the end time
            function checkTime() {{
                if (audioPlayer.currentTime >= {end_time}) {{
                    audioPlayer.pause();
                    audioPlayer.currentTime = {end_time};  // Optionally set to end time
                    audioPlayer.removeEventListener('timeupdate', checkTime);
                }}
            }}
            // Event listener to check the current time against end time
            audioPlayer.addEventListener('timeupdate', checkTime);
        }});
    </script>
    """
    return audio_html


def jump_player():
    st.session_state.audio_player = st.session_state["audio_cont"].audio(st.session_state.audio, format="audio/wav",
                                                                         start_time=st.session_state.start_time,
                                                                         end_time=st.session_state.end_time)


# Function to display audio player
def display_audio_player(cont):
    if 'audio_file' in st.session_state:
        cont.markdown("**Player**")
        # Display audio player
        col1, col2 = cont.columns([2, 15])
        with col2:
            st.audio(st.session_state.audio_bytes, format=st.session_state.audio_format,
                     start_time=st.session_state.get('start_time', 0))  # , key=audio_key)

        # Manage playback times
        if 'playback_times' not in st.session_state:
            st.session_state.playback_times = {}
        with col1:
            st.session_state.playback_times["0"] = 0
            if st.button("⏪", key="0"):
                # Set the start time and increment the key to force re-render of the audio player
                st.session_state.start_time = 0
                st.rerun()

    if "start_time" not in st.session_state:
        st.session_state.start_time = 0
    if "end_time" not in st.session_state:
        st.session_state.end_time = None
    cont.divider()

def show_quiz(cont):
    quiz = st.session_state["quiz"]
    if quiz is not None:
        score = 0
        quiz_arr = quiz.split("\n\n")
        valid = 0
        # Iterate through each question
        for block in quiz_arr:
            q_a = block.split('\n')
            if len(q_a) < 2:
                continue
            if (len(q_a[0]) == 0):
                q_a = q_a[1:]
            question = q_a[0]
            question_body = question.split(';')[1].strip()
            cont.markdown(f"***{valid + 1}: {question_body}***")
            choices = q_a[1:]
            choices_arr = []
            correct_arr = []
            for answer in choices:
                choice_arr = answer.split(";")
                if len(choice_arr) == 1:
                    choice = choice_arr[0].strip()
                    if choice.find('*') == 0:  # correct
                        choice = choice[1:]
                        correct_arr.append(choice)
                    choices_arr.append(choice)

                elif len(choice_arr) > 1:
                    choices_arr.append(choice_arr[1].strip())
                    if choice_arr[0].find("*") >= 0:
                        correct_arr.append(choice_arr[1].strip())
            # Allow multiple answers using multiselect
            selected_answers = cont.multiselect("Select all that apply", choices_arr)
            valid += 1

            # # Display selected answers
            if len(selected_answers):

                res = collections.Counter(correct_arr) == collections.Counter(selected_answers)
                if res:
                    pref = ':green[**Correct!**]'
                    score += 1

                else:
                    pref = ':red[**Oops. Try again**]'

                cont.markdown(f"**Question {valid + 1}**. {pref}: You selected: {selected_answers}")
        cont.markdown(f"<h2 style='font-size:26px;'>Total score: {score}/{valid}</h2>", unsafe_allow_html=True)

    # Function to handle link click
def link_click(item):
    if item:
        start_secs, end_secs = range2start_end(item.strip())
        st.session_state.start_time = start_secs




def show_concepts(cont, tags):
    with cont:
        tags_column = []
        times_column = []
        for tag, times in tags.items():
            l = len(times)
            tags_column.append(tag)
            times_list = []
            for i, tim in enumerate(times):
                start_secs, end_secs = range2start_end(tim.strip())
                key = f'{tag}_{tim}'
                st.session_state.playback_times[key] = start_secs
                tim_dict={}
                tim_dict['name']=tim
                tim_dict['url']=tim
                times_list.append(tim_dict)
            times_column.append(times_list)

            data = {
                'tags': tags_column,
                'times': times_column,
            }

        df = pd.DataFrame(data)
        # Generate HTML content for the links
        html_content = """
           <style>
               table {
                   width: 100%;
                   border-collapse: collapse;
               }
               th, td {
                   border: 1px solid #ddd;
                   padding: 8px;
               }
               th {
                   padding-top: 12px;
                   padding-bottom: 12px;
                   text-align: left;
                   background-color: #f2f2f2;
               }
               a {
                   text-decoration: none;
                   color: blue;
               }
           </style>
           <table>
               <tr>
                   <th>Concepts</th>
                   <th>Times</th>
               </tr>
           """

        for _, row in df.iterrows():
            html_content += f"<tr><td>{row['tags']}</td><td>"
            for link_dict in row['times']:
                html_content += f'<a href="#" id="{link_dict["name"]}">{link_dict["name"]}</a> '
            html_content += "</td></tr>"
        html_content += "</table>"
        # Use click_detector to capture clicks
        clicked = click_detector(html_content)

    # Display the clicked item if any
    if clicked and clicked!=st.session_state['prev_click']:
        link_click(clicked)
        st.session_state['prev_click']=clicked
        st.rerun()



def get_body(str):
    # Find the index of the substring
    substring_to_find = "Result:"
    index = str.find(substring_to_find)

    if index != -1:
        # Calculate the starting index of the substring after the found substring
        start_index = index + len(substring_to_find)
        # Extract the substring from start_index to the end
        result_string = str[start_index:]
    else:
        result_string = str

    return (result_string)


def locate_tts_file():
    tts_file = st.session_state.config.tts_file
    return tts_file
    # ttsmp3 = os.path.join(st.session_state['dir'], "ttsmp3.mp3")
    # if os.path.isfile(ttsmp3):
    #    expd.markdown(get_binary_file_downloader_html('media/short.mp3', 'Audio'), unsafe_allow_html=True)
def load_AI(cont,sb):
   # if 'dir' in st.session_state and st.session_state['dir'] != None:
        # short = find_short_summary()
    #    short = find_body_of("Short_Summary")\
    short = st.session_state["short_summary"]
    if short is not None:
        expd = cont.expander("Short Summary", expanded=True, icon="💥")
        expd.subheader("Short Summary")
        expd.markdown(f'<div style="text-align: right;">{short}</div>', unsafe_allow_html=True)
        if st.session_state.allow_tts_download:
            tts_location = locate_tts_file()
            if tts_location is not None and os.path.isfile(tts_location):
                expd.markdown(get_binary_file_downloader_html(tts_location, 'Audio'), unsafe_allow_html=True)

    mindmap = st.session_state['mindmap']
    if mindmap is not None:
        expd = cont.expander("MindMap", expanded=False, icon="🦉")
        expd.subheader("Mind Map")
        expd.image(mindmap, caption='MindMap of the Lesson')

    concepts = st.session_state['concepts']
    if concepts is not None:
        st.session_state["concepts_expd"] = sb.expander("Key Concepts", expanded=True, icon="🏹")
        st.session_state["concepts_expd"].subheader("Key Concepts")
        tags = extract_tags()
        if tags is not None:
            show_concepts(st.session_state["concepts_expd"], tags)

    long = st.session_state["long_summary"]
    if long is not None:
        expd = cont.expander("Long Summary", expanded=False, icon="📜")
        expd.subheader("Long Summary")
        expd.markdown(f'<div style="text-align: right;">{long}</div>', unsafe_allow_html=True)
        # expd.markdown(long)

    quiz = st.session_state["quiz"]
    if quiz is not None:
        expd = cont.expander("Quiz", expanded=False, icon="❓")
        expd.subheader("Self Evaluation Quiz")
        show_quiz(expd)

    additional = st.session_state["additional"]
    if additional is not None:
        expd = cont.expander("Additional Reading", expanded=False, icon="📚")
        expd.subheader("Additional Reading")
        expd.markdown(f'<div style="text-align: right;">{additional}</div>', unsafe_allow_html=True)

    st.session_state["ai"] = True


def init():
    st.session_state.config = aaFrontConfig()
    st.session_state.config.parse_file()

    # Initialize session state for clicked item if not exists
    if 'clicked_item' not in st.session_state:
        st.session_state.clicked_item = None
    #if 'dir' not in st.session_state:
     #   st.session_state["dir"] = None
    if 'jump' not in st.session_state:
        st.session_state["jump"] = 0
    if 'ai' not in st.session_state:
        st.session_state["ai"] = False
    if 'short_summary' not in st.session_state:
        st.session_state["short_summary"] = None
    if 'long_summary' not in st.session_state:
        st.session_state["long_summary"] = None
    if 'concepts' not in st.session_state:
        st.session_state["concepts"] = None
    if 'mindmap' not in st.session_state:
        st.session_state["mindmap"] = None
    if 'quiz' not in st.session_state:
        st.session_state["quiz"] = None
    if 'additional' not in st.session_state:
        st.session_state["additional"] = None
    if 'audio' not in st.session_state:
        st.session_state["audio"] = None
    if 'audio_player' not in st.session_state:
        st.session_state["audio_player"] = None
    if 'concepts_expd' not in st.session_state:
        st.session_state["concepts_expd"] = None
    if 'audio_cont' not in st.session_state:
        st.session_state["audio_cont"] = None
    if 'playback_times' not in st.session_state:
        st.session_state.playback_times={}
    if 'allow_tts_download' not in st.session_state:
        st.session_state.allow_tts_download = False
    if 'prev_click' not in st.session_state:
        st.session_state.prev_click=None

# Streamlit app
def main():
    if 'ai' not in st.session_state or st.session_state["ai"] == False:
        init()
    st.title("Aaron The Owl")
    st.subheader("Lecture Recap")
    player_placeholder = st.empty()
    cont = player_placeholder.container()
    # if 'dir' not in st.session_state or st.session_state["dir"] == "":
    m_container,sb = st.columns([500, 210])
    with st.popover("Settings"):
        config_file = st.file_uploader("Upload a config file", type=['cfg'])
        st.session_state.allow_tts_download = st.checkbox("Summary as MP3")

    if config_file is not None:
        # Read the content of the uploaded file
        file_content = config_file.read()
        # Convert bytes content to a file-like object

        file_like_object = io.StringIO(file_content.decode('utf-8'))
        st.session_state.config.parse_io(file_like_object)

    load_files(cont)
    # if  'dir' in st.session_state and st.session_state["dir"] != "":
    display_audio_player(cont)
    # if 'ai' not in st.session_state or st.session_state["ai"] == False:
    load_AI(m_container,sb)

if __name__ == "__main__":

    main()
