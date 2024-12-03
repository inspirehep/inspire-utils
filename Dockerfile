FROM python:2.7.18-buster


COPY . .

# RUN python2.7 -m pip install -e .[tests]

CMD ["/bin/bash"]
