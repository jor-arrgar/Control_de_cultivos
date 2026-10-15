import streamlit as st


# MARK: Main function for accesibility options
def accesibility(show_strings=False):
    '''Sets the accessibility options for the app.'''


    with st.sidebar.expander('Accesibilidad'):

        style_string = "<style>body {"
        style_string += set_mayus_letters()
        style_string += daltonism()
        

        style_string += "}</style>"
        st.html(style_string)
        if show_strings:
            st.text(style_string)

        direct_execution_strings = []
        direct_execution_strings.extend(increase_font_size())
        
        for direct_execution_string in direct_execution_strings:
            st.html(f"<style>{direct_execution_string}</style>")

            if show_strings:
                st.text(direct_execution_string)
            #st.write(direct_execution_strings)



# MARK: All mayus
def set_mayus_letters():
    if st.checkbox("Todo en mayúsculas"):
        return "text-transform: uppercase;"
    return ""


# MARK: Increase font size
def increase_font_size(min_=16, max_=20):
    testid_list = [
        'stMarkdownContainer',      # st.markdown content
        'stBlock',                   # Block-level containers
        'stAppFrame',                # Main app frame
        'stVerticalBlock',          # Vertical blocks
        'stHorizontalBlock',         # Horizontal blocks (wide layout)
        'stContainer',               # Generic containers
        'stAlert',                   # Alert boxes
        'stButton',                  # Buttons and widgets
        'stForm',                    # Forms
    ]

    selectors = []
    
    for testid in testid_list:
        # Match elements WITH the data-testid attribute AND its value
        selector = f'[data-testid="{testid}"]'
        selectors.append(selector)
    
    # Combine all selectors into one group with commas between them
    combined_selector = ', '.join(selectors)
    
    if st.checkbox("Aumentar tamaño de fuente"):
        # Apply large font size (30px)
        return f"{combined_selector} {{ font-size: {max_}px !important; }}", \
               "body {{ font-size: {max_}px !important; }}"
    
    else:
        # Default font size (16px)
        return f"{combined_selector} {{ font-size: {min_}px !important; }}", \
               "body {{ font-size: {min_}px !important; }}"
    

# MARK: Daltonism
def daltonism():
    if st.checkbox("Daltonismo", disabled=True, help="This option is not yet implemented."):
        return ""
    return "" 