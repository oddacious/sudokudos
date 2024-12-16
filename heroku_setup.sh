mkdir -p ~/.streamlit/
cp ./.streamlit/config.toml ~/.streamlit/config.toml

echo "\n\
[server]\n\
headless=true\n\
port=$PORT\n\
" >> ~/.streamlit/config.toml