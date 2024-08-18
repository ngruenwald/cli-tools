FROM debian:bookworm-slim

RUN apt-get update \
 && apt-get -y install \
      bash-completion \
      command-not-found \
      curl \
      file \
      git \
      iproute2 \
      locales \
      ncurses-bin \
      procps \
      python3 \
      python3-requests \
      stow \
      sudo \
      tar \
      tmux \
      unzip \
      xz-utils \
      zsh


ENV PATH=${PATH}:/opt/local/bin

RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.UTF-8

ARG SHELL=zsh

RUN useradd --user-group --system --groups sudo --create-home --no-log-init --shell /bin/${SHELL} user
RUN passwd -d user

RUN mkdir /opt/local && chown user /opt/local

USER user
WORKDIR /home/user


COPY . /tmp/cli-tools
RUN cd /tmp/cli-tools \
 && python3 clitools.py install \
      bat \
      bottom \
      eza \
      fd \
      fzf \
      gtrash \
      helix \
      neovim \
      powerline-go \
      ripgrep \
      runme \
      starship \
      yazi \
      zoxide \
      zsh-autosuggestions \
      zsh-command-not-found \
      zsh-completions \
      zsh-fzf-tab \
      zsh-history-substring-search \
      zsh-syntax-highlighting \
      zsh-you-should-use \
 && echo rm -rf /tmp/cli-tools


ENV SHELL "/bin/${SHELL}"

# COPY dotfiles /home/user/.dotfiles
# RUN chown user:user -R /home/user/.dotfiles

# RUN mkdir /home/user/.config /home/user/.cache /home/user/.local \
#  && cd /home/user/.dotfiles \
#  && stow --target /home/user/.config . \
#  && printf "\nsource ~/.config/shell/bashrc\n" >> /home/user/.bashrc \
#  && printf "\nsource ~/.config/shell/zshrc\n" >> /home/user/.zshrc

# ENV PLATFORM=d12

CMD $SHELL
