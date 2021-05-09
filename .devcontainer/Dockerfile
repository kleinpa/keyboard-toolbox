FROM debian:testing-20201012-slim

# Install Bazel and Node dependencies along with Git
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
   && apt-get install --no-install-recommends -y \
   ca-certificates \
   curl \
   g++ \
   git \
   gnupg2 \
   python3 \
   python-is-python3 \
   unzip \
   zip \
   && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/library-scripts

# Install bazelisk and ibazel
RUN curl -s https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - \
   && echo 'deb https://deb.nodesource.com/node_12.x bullseye main' > /etc/apt/sources.list.d/nodesource.list \
   && apt-get update && export DEBIAN_FRONTEND=noninteractive && apt-get install -y --no-install-recommends \
   nodejs \
   && rm -rf /var/lib/apt/lists/* \
   && npm install --global @bazel/bazelisk@1.8.1 @bazel/ibazel@0.15.10

# Install buildifier
RUN mkdir /tmp/buildifier \
   && cd /tmp/buildifier \
   && curl https://github.com/bazelbuild/buildtools/archive/3.5.0.tar.gz -sLo- | tar xzvf - --strip-components=1 \
   && echo 3.6.0 > .bazelversion \
   && bazel build -c opt //buildifier && bazel shutdown \
   && cp $(bazel info -c opt bazel-bin)/buildifier/linux_amd64_stripped/buildifier /usr/local/bin \
   && bazel clean --expunge

# Install Kicad build deps
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
   && apt-get install --no-install-recommends -y \
   cmake \
   libgl-dev \
   libglew-dev \
   libglm-dev \
   libcurl4-openssl-dev \
   libcairo2-dev \
   libboost-dev swig \
   libwxgtk3.0-gtk3-dev \
   libgtk-3-dev \
   libssl-dev \
   libboost-test-dev \
   libboost-filesystem-dev \
   build-essential \
   libpython3-dev \
   && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/library-scripts

