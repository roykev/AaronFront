import collections
import streamlit as st
import tempfile
from pydub import AudioSegment

from utils.aa_utils import find_txt, get_audio_file_content, get_binary_file_downloader_html, range2start_end, set_svg_text_direction

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
        # if u_file.type == 'audio/mpeg':
        #     with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        #         tmp_file.write(u_file.getvalue())
        #         tmp_file_path = tmp_file.name
        #         # Read the audio file
        #         st.session_state.audio = AudioSegment.from_mp3(tmp_file_path)
        #         st.session_state.audio_file = u_file.name
        #         st.session_state.audio_bytes = u_file.getvalue()
        #         st.session_state.audio_format = u_file.type.split('/')[-1]
        if  'text' in u_file.type:
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




#    col1.write('Please select a folder:')
 #   clicked = col2.button('Folder Picker')
  #  if clicked:
   #     dir = filedialog.askdirectory(master=root, initialdir="./")
    #    st.session_state.dir = dir
    #  audio = find_audio(dir)
    # st.session_state.audio=audio
    #return col1


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
    # File uploader
    # uploaded_files = cont.file_uploader("Choose an audio file (mp3), and AI outputs", accept_multiple_files=True)
    # if uploaded_files is not None and len(uploaded_files)>0:
    #     st.session_state.audio_file = uploaded_files
    #     st.session_state.audio_bytes = uploaded_files.getvalue()
    #     st.session_state.audio_format = uploaded_files.type.split('/')[-1]
    # audio = st.session_state.audio

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

def show_concepts(cont, tags):
    if cont is not None:
        for tag, times in tags.items():
            l = len(times)
            columns = cont.columns(l + 1)
            with columns[0]:
                cont.markdown(f"**{tag}**: ")
            for i, tim in enumerate(times):
                with columns[i + 1]:
                    start_secs, end_secs = range2start_end(tim.strip())
                    key = f'{tag}_{tim}'
                    st.session_state.playback_times[key] = start_secs
                    #    if key not in st.session_state:
                    if st.button(tim, key=key):
                        st.session_state["start_time"] = start_secs
                        st.rerun()
            cont.divider()


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


# def find_body_of(task):
#     body = None
#     if 'dir' in st.session_state or st.session_state['dir'] != '':
#         file_name = find_txt(st.session_state["dir"], task)
#         if file_name is not None:
#             f = io.open(file_name, mode="r", encoding="utf-8")
#             content = f.read()
#             body = get_body(content)
#             f.close()
#         return body


def load_AI(cont):
   # if 'dir' in st.session_state and st.session_state['dir'] != None:
        # short = find_short_summary()
    #    short = find_body_of("Short_Summary")\
    short = st.session_state["short_summary"]
    if short is not None:
        expd = cont.expander("Short Summary", expanded=True, icon="💥")
        expd.subheader("Short Summary")
        expd.markdown(f'<div style="text-align: right;">{short}</div>', unsafe_allow_html=True)
       #TODO ttsmp3 = os.path.join(st.session_state['dir'], "ttsmp3.mp3")
    #TODO    if os.path.isfile(ttsmp3):
         #TODO   expd.markdown(get_binary_file_downloader_html('media/short.mp3', 'Audio'), unsafe_allow_html=True)
    mindmap = st.session_state['mindmap']
    if mindmap is not None:
        expd = cont.expander("MindMap", expanded=False, icon="🦉")
        expd.subheader("Mind Map")
        expd.image(mindmap, caption='MindMap of the Lesson')

    concepts = st.session_state['concepts']
    if concepts is not None:
        st.session_state["concepts_expd"] = cont.expander("Key Concepts", expanded=False, icon="🏹")
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


# Streamlit app
def main():
    if 'ai' not in st.session_state or st.session_state["ai"] == False:
        init()

    sb, m_container = st.columns([1, 100])
    m_container.title("Aaron The Owl")
    m_container.subheader("Lecture Recap")
    player_placeholder = m_container.empty()
    cont = player_placeholder.container()
    # if 'dir' not in st.session_state or st.session_state["dir"] == "":
    load_files(cont)

    # if  'dir' in st.session_state and st.session_state["dir"] != "":
    display_audio_player(cont)
    # if 'ai' not in st.session_state or st.session_state["ai"] == False:
    load_AI(m_container)

if __name__ == "__main__":
    main()
