
### Exporting slides to html and pdf

You can export your RISE presentation to PDF using the following steps:

1. Generate the slides and serve them using nbconvert:
```bash
jupyter nbconvert --to slides jupyterhub_webinar23.ipynb --post serve
```
2. Open up a webpage in the browser at `http://127.0.0.1:8000/jupyterhub_webinar23.slides.html#/`

3. Run the following command:
```bash
google-chrome --headless --print-to-pdf=jupyterhub_webinar23.pdf http://127.0.0.1:8000/jupyterhub_webinar23.slides.html?print-pdf
```

For more information read [RISE documentation](https://rise.readthedocs.io/en/latest/exportpdf.html).

