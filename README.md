# CLI Tools

This started out as a test for my dotfiles. _Things escalated quickly..._

The [packages](packages) subfolder contains configurations for various CLI tools.

Currently only tools that can be run without dependencies are supported. So no
interpreted things (python, javascript, etc.) and no tools with OS dependencies.
Right now this covers mostly Rust and Golang stuff, with a few shell scripts added
to the mix.

With the __clitools.py__ script you can download and install these packages on x86_64 Linux.

If you are missing __clitools.py__, then you need to execute the following:

```.sh
python code/_amalgate.py
```

This will create the amalgated script from the source files.
