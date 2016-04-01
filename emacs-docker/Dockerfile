FROM ubuntu:16.04
MAINTAINER gdiener@cardinalpeak.com

#
# Initial definitions
#
# User account to create
ENV USER grd
# Email and name for git commands
ENV USER_GIT_EMAIL gdiener@cardinalpeak.com
ENV USER_GIT_NAME  Glen Diener

# need libgl1-mesa-glx for emacs to run in a window
RUN \
  apt-get update && apt-get install -y \
  build-essential \
  openssh-server \
  emacs \
  sudo \
  ssh \
  libgl1-mesa-glx


# create su-able, password-less account for $USER
RUN addgroup --system ${USER}
RUN adduser --system --shell /bin/bash --gecos '${USER}' \
  --uid 1000 --disabled-password --home /home/${USER} ${USER}
RUN adduser ${USER} sudo
RUN echo ${USER}:${USER} | chpasswd
RUN echo "${USER} ALL=NOPASSWD:ALL" >> /etc/sudoers

ENV HOME /home/${USER}
WORKDIR /home/${USER}

# Create a mount point for external file systems, /ex.
# Note: this will fail on windows.
RUN mkdir /ex
VOLUME /ex

# Set up ssh...we don't use it, but could.
EXPOSE 22
RUN mkdir -p /var/run/sshd
RUN echo 'X11Forwarding yes' >> /etc/ssh/ssh_config

# ...I prefer to start emacs, and use its shell:
USER ${USER}
ENTRYPOINT ["/usr/bin/emacs"]
#ENTRYPOINT ["/bin/bash"]
COPY DOT_EMACS /home/${USER}/.emacs
COPY DOT_BASH_RC /home/${USER}/.bashrc
RUN sudo chown ${USER}.nogroup /home/${USER}/.emacs ; \
    sudo chown ${USER}.nogroup /home/${USER}/.bashrc ;


