# WebDeployer
Framework for instantly deploying web servers on arbitary Linux devices. These files are intended to be a baseline for developing any project that requires a webserver. The repository contains scripts for building servers, tearing down servers, customizable config files, a template for Python webhooks server-side, and templates for HTML, JavaScript, and CSS on the client-side. 

### How to use
Clone this repository, edit the templates as needed, and run `bash build.sh` to deploy a new webserver. Re-running `bash build.sh` will overwrite/rebuild the server. Run `bash teardown.sh` to delete the server.

### build.sh
Script that deploys a new web server. Sets up RSA keys, installs Python dependencies, sets up a Python virtual environment, creates a systemd service that hosts a uvicorn web server over HTTPS, and starts the server.

### teardown.sh
Script that gracefully shuts down the systemd service and deletes everything, including the RSA keys, the virtual environment, the systemd service, and all scripts in the deployment directory. The dev directory (the git directory) remains untouched.

### requirements.txt
Required Python packages. Must be present in order to run.

### project.conf
Edit this configuration file to change the project name, install directories, and other customizable aspects.

### service.template
Template for the systemd service. Default settings will work, but these can be edited if needed.

### main.py
Template that provides Python webhooks for the deployed server. Fill in the webhooks to define server-side behavior.

### dashboard.html
Template for the client-side HTML file. Edit this to define client-side structure/display.

### style.css
Template to customize the style of the client-side HTML page.

### script.js
Template to define the behavior of client-side software.
