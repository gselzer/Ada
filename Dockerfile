FROM mambaorg/micromamba:1.4.1
ARG MAMBA_DOCKERFILE_ACTIVATE=1
COPY . ./
RUN micromamba create -n ada && \
  micromamba install -y -n ada -f environment.yml && \ 
  micromamba clean --all --yes
CMD ["flask", "--app", "ada", "run", "--host", "0.0.0.0"]