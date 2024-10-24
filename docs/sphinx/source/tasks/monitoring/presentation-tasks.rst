******************
Presentation Tasks
******************

Markdown
===============

Mapped to ``ece.mon.presentation.markdown``.

This presentation task creates a Markdown file which contains visualizations of the created diagnostics on disk.

**Required arguments**

* ``src``: A list of strings containing paths to the diagnostics on disk that should be presented.
* ``dst``: A string containing the path to the directory where the report should be put. The directory will contain the image files for the presentation, as well as a file ``summary.md`` with the final presentation.
* ``template``: A string containing the path to the Markdown template file. An exemplary file is contained in the ``docs/template`` folder in the repository_.

::

    - ece.mon.presentation.markdown:
        src:
            - "{{mondir}}/description.yml"
            - "{{mondir}}/exp-id.yml"
            - "{{mondir}}/output-disk-usage.yml"
            - "{{mondir}}/tos-global-avg.nc"
            - "{{mondir}}/sos-global-avg.nc"
        dst: "{{mondir}}/report"
        template: "scriptengine-tasks-ecearth/docs/templates/markdown_template.md.j2"

.. _custom-visualization:

Custom Visualization Options
#############################

For custom visualization, a dictionary instead of the path alone can be passed as a source.
The path then must lie at the key ``path``.
Currently, the following customization features are implemented:

* ``value_range``: set the minimum and maximum value of a time series or (temporal) map. Particularly useful for temporal maps. Default: ``[None, None]``
* ``colormap``: set a custom colormap for maps and temporal maps. Default: ``RdBu_r``. The list of possible colormaps is in the `Matplotlib documentation`_.
* ``reference``: provide a dict with keys ``value`` and optionally ``label`` for a reference value to be shown in the time series. Default: ``None``. 

Example::

    - ece.mon.presentation.markdown
        src:
            - "{{mondir}}/description.yml"
            - "{{mondir}}/exp-id.yml"
            - "{{mondir}}/output-disk-usage.yml"
            - path: "{{mondir}}/tos_nemo_global_mean_year_mean_timeseries.nc"
              value_range: [13, 17]
            - path: "{{mondir}}/tos_nemo_year_mean_temporalmap.nc"
              value_range: [-2, 30]
              colormap: 'viridis'
            - path: "{{mondir}}/tas_nemo_global_mean_year_mean_timeseries.nc"
              reference:
                value: 14.4
                label: "ERA5 (1991-2020)"
            - path: "{{mondir}}/pr_nemo_global_mean_year_mean_timeseries.nc"
              reference: {"value":2.93, "label":"ERA5 (1991-2020)"}
        dst: "{{mondir}}/report"
        template: "scriptengine-tasks-ecearth/docs/templates/markdown_template.md.j2"


Redmine
==============

Mapped to ``ece.mon.presentation.redmine``.

This presentation task creates a Redmine issue on the EC-Earth development portal, containing visualizations of the created diagnostics on disk.

**Required arguments**

* ``src``: A list of strings containing paths to the diagnostics on disk that should be presented. You can use the :ref:`custom-visualization` in the same way as with the Markdown task.
* ``local_dst``: A string containing the path to the directory where the attachments can be stored locally. The directory will contain the image files for the presentation, as well as a file ``issue_description.txt`` with the issue description text.
* ``template``: A string containing the path to the issue description template file. An exemplary file is contained in the ``docs/template`` folder in the repository_.
* ``api_key``: Your API key for logging in to the EC-Earth development portal. You can find it (you might have to generate it first) in your `account settings`_.
* ``subject``: The name of your issue. A recommended format for this is shown below.

::

    - ece.mon.presentation.redmine:
        src:
            - "{{mondir}}/description.yml"
            - "{{mondir}}/exp-id.yml"
            - "{{mondir}}/sim-years.yml"
            - "{{mondir}}/tos-global-avg.nc"
            - "{{mondir}}/sos-global-avg.nc"
            - "{{mondir}}/sithic-north-mar.nc"
            - "{{mondir}}/sithic-north-sep.nc"
        local_dst: "{{mondir}}/redmine-report"
        api_key: # Your API key for the EC-Earth Dev Portal
        subject: "{{exp_id}}: Short Description"
        template: "scriptengine-tasks-ecearth/docs/templates/redmine_template.txt.j2"

.. _repository: https://github.com/uwefladrich/scriptengine-tasks-ecearth/tree/master/docs/templates
.. _account settings: https://dev.ec-earth.org/my/account
.. _Matplotlib documentation: https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html