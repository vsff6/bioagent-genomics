FROM continuumio/miniconda3:24.1.2-0

WORKDIR /app

COPY env/environment.yml .
RUN conda env create -f environment.yml && conda clean -afy

COPY . .

SHELL ["conda", "run", "-n", "genomics-agent", "/bin/bash", "-c"]

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "genomics-agent"]
CMD ["bash", "examples/run_tiny_demo.sh"]
