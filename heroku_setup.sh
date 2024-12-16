mkdir -p ~/.streamlit/
cp ./.heroku/streamlit_config.toml ~/.streamlit/config.toml

echo $PORT
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' 's/port=.*/port='$PORT'/' ~/.streamlit/config.toml
else
    sed -i 's/port=.*/port='$PORT'/' ~/.streamlit/config.toml
fi