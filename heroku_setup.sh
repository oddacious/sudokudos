mkdir -p ~/.streamlit/
cp ./.heroku/streamlit_config.toml ~/.streamlit/config.toml

echo $PORT
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' 's/port=.*/port='$PORT'/' ~/.streamlit/config.toml
else
    sed -i 's/port=.*/port='$PORT'/' ~/.streamlit/config.toml
fi

# Patch Streamlit's index.html for better Google search appearance
STREAMLIT_INDEX=$(python -c "import streamlit; import os; print(os.path.join(os.path.dirname(streamlit.__file__), 'static', 'index.html'))")
sed -i "s|<title>Streamlit</title>|<title>Sudokudos - Solvers, scores, and snazzy charts</title>|g" "$STREAMLIT_INDEX"
sed -i "s|</title>|</title><meta name=\"description\" content=\"Explore results, rankings, and solver performance from the World Sudoku Championship (WSC) and Sudoku Grand Prix (GP).\">|g" "$STREAMLIT_INDEX"