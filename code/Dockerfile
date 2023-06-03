FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

RUN pip3 install jupyter
RUN pip3 install pandas
RUN pip3 install requests
RUN pip3 install ipywidgets
RUN pip3 install ipyleaflet
RUN pip3 install ipython
RUN pip3 install geopy
RUN pip3 install geopy
RUN pip3 install voila


WORKDIR /notebooks

COPY *.ipynb /notebooks/

EXPOSE 8888

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root"]