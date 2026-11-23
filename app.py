
import streamlit as st

from assistant_core import run_turn, MAX_HISTORY

from langchain_core.messages import (
    HumanMessage,
    AIMessage
)


# ---------------------------------------
# 1. STREAMLIT PAGE SETTINGS
# ---------------------------------------

st.set_page_config(
    page_title="StudyMate",
    page_icon="📚",
    layout="centered"
)

st.title("📚 StudyMate")
st.caption("Your personal AI Study Planner Assistant")


# ---------------------------------------
# 2. SIDEBAR - API KEY
# ---------------------------------------

with st.sidebar:

    st.header("Gemini API Key")

    api_key = st.text_input(
        "Enter your Gemini API key",
        type="password"
    )

    st.caption(
        "Get your API key from Google AI Studio."
    )

    st.divider()

    st.subheader("Available Tools")

    st.write("1. Days Until Exam")
    st.write("2. Split Study Hours")

    if st.button("Clear Chat"):

        st.session_state.chat = []

        st.rerun()


# ---------------------------------------
# 3. CREATE CHAT HISTORY
# ---------------------------------------

if "chat" not in st.session_state:

    st.session_state.chat = []


# ---------------------------------------
# 4. DISPLAY PREVIOUS MESSAGES
# ---------------------------------------

for message in st.session_state.chat:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            tools = message.get("tools", [])

            with st.expander("Tools used"):

                if tools:
                    for tool_name in tools:
                        st.write("✓", tool_name)

                else:
                    st.write("No tools used.")


# ---------------------------------------
# 5. GET NEW USER QUESTION
# ---------------------------------------

user_question = st.chat_input(
    "Ask me about your studies..."
)


if user_question:

    # Display user question
    st.session_state.chat.append({
        "role": "user",
        "content": user_question
    })

    with st.chat_message("user"):
        st.markdown(user_question)


    # Check whether API key is provided
    with st.chat_message("assistant"):

        if not api_key.strip():

            answer = (
                "Please enter your Gemini API key "
                "in the sidebar."
            )

            used_tools = []

        else:

            try:

                # --------------------------------
                # 6. CONVERT CHAT TO LANGCHAIN MESSAGES
                # --------------------------------

                history = []

                previous_messages = (
                    st.session_state.chat[:-1][-MAX_HISTORY:]
                )

                for message in previous_messages:

                    if message["role"] == "user":

                        history.append(
                            HumanMessage(
                                content=message["content"]
                            )
                        )

                    elif message["role"] == "assistant":

                        history.append(
                            AIMessage(
                                content=message["content"]
                            )
                        )


                # --------------------------------
                # 7. CALL AI ASSISTANT
                # --------------------------------

                with st.spinner("StudyMate is thinking..."):

                    answer, used_tools = run_turn(
                        api_key,
                        history,
                        user_question
                    )

            except Exception as error:

                # Do not display or print the API key
                answer = (
                    f"Something went wrong: "
                    f"{type(error).__name__}. "
                    "Please check your API key, quota "
                    "or model availability."
                )

                used_tools = []


        # Display AI answer
        st.markdown(answer)


        # Display tools used
        with st.expander("Tools used"):

            if used_tools:

                for tool_name in used_tools:
                    st.write("✓", tool_name)

            else:
                st.write("No tools used.")


    # --------------------------------
    # 8. SAVE CONVERSATION
    # --------------------------------

    st.session_state.chat.append({

        "role": "assistant",

        "content": answer,

        "tools": used_tools

    })
