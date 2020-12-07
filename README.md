# Jupyter Extra Magics

Starting working with Jupyter - we declared basic functionality needed to make Jupyter interactive and ready for processing data.   

All magics are agnostic to kernel type  and should work on any kernel. Notice that using variables in the magic should declared in python3 context - that means that if you’re using python3 kernel all variables are available in the magic, if you’re using other kernel (PySpark,Spark) you should declare variables with the %%local magic. note that you can apply multiple magics and chain them together.

### Read more with practical examples:

https://benm-23166.medium.com/jupyter-helpful-extra-magics-9545075f3138

# Installation:

Install the package using pip (python > 3.6)
```
pip install jupyter_extra_magics
```
Or using the github repo:

```
git clone https://github.com/benmizrahi/jupyter-extra-magics.git && cd jupyter-extra-magics && python3 setup.py sdist bdist_wheel && pip install dist/pdp_extra_magics*.whl
```
After having the package installed, you need to modify jupyter_notebook_config.py to autoload the magics when Jupyter instance is loaded:

```
c = get_config()
c.InteractiveShellApp.extensions = ['extra_magics']
```

Once you configure that, the extra magics are ready to use inside Jupyter instance.

# Declarations: 

## Estimate Magic:  

An estimation magic for BQ, this magic can give you the estimated cost & scan of a query usage and parameters:

####  Declaration:

```
%%estimate
optional params: 
   block_cost -
          decimal/integer cost ($) blocker to run the query, 
          if cost is above the amount, Y/N question will be display
   block_scan -
          integer (GB) blocker to run the query, 
          if scan is above the amount, Y/N question will be display
    dry-run -
          Boolean - If the current cell contains %%bigquery magic ?
```

----
## Notifier Magic:  

A magic designed to collect cell execution results and combine notebook results into single EMAIL/SLACK, the magic run immediate and it give us the ability to debug the message while development, each cell output is acceptable as an attachment - Datafream,  Plot, String messages.

Using this magic requires having 4 environment parameters declared in the Jupyter instance created:  

```
SLACK_API_TOKEN - sending slack notification using slack sdks for python.read more about the web-token inside slack repo link: (https://github.com/slackapi/python-slack-sdk)   

EMAIL_USER - username for smtp connection to send email.   

EMAIL_PASS - password for smtp connection to send email.   

ENV- current running environment (INT/PROD/INTERACTIVE)
```

####  Declaration:

```
%%notify_collect 
   kind:
      EMAIL|SLACK - what is the type of the message we want to send
   destination:
      String - how should we notify, a comma separated list 
      of destinations (example: "email@address.com") or comma    
      separated channels (example: #channel,#channel_two)
   header:
      String - the EMAIL header message 
   body:
      String - the email body (will be append before the result-set).

%notify_clean - cleaning the mails loaded until now

%notify 
    show_env - is the env value should be visible in the message header 
    ([INTERACTIVE]|[INT][PROD])
```

## SuperRun Magic:

A magic that enables the ability to run notebook from another notebook, this magic enables us to split the notebooks into sub notebooks and execute them in the same kernel. this is really effective and enables us to create more modular and splittable notebooks . this magic is also working on interactive mode, getting the needed notebook directly from github 

**Notice! path to the notebook should be full path in you're local environment not relative!  

```
%super_run 
    notebook: 
        String, full path the the notebook location.
        (example: /full/path/to/other/notebook.ipynb)
    regex_filter: 
        String, declared regex for the content of the cell, means that if the if the regex pattern
        exists in the cell, the cell will be executed, if not it will be skip execution.
        this regex enable us to write "GENERIC" notebook in multiple kernel types, and 
        use them where needed.
```


# Contributing

To learn how to setup a development environment and for contribution guidelines, see CONTRIBUTING.md.   




# Copyright
See LICENSE for details. Copyright (c) 20202 Ben Mizrahi