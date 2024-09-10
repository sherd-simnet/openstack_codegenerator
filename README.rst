=======================
OpenStack CodeGenerator
=======================

Primary goal of the project is to simplify maintainers life by generating
complete or at least parts of the code.

CodeGenerator is able to generate OpenAPI specs for certain services by
inspecting their code and API Reference (api-ref) documentation. This requires
the service package be installed in the environment where the generator is
running. The generator then tries to initialize the service application and for
supported services scans for the exposed operations. At the moment the
following services are covered:

- Nova
- Neutron
- Cinder
- Glance
- Keystone
- Octavia

Getting started
---------------

CodeGenerator is not currently packaged on PyPI (and may never be). As a
result, you must install from Git. For example:

.. code-block:: shell

    $ git clone https://opendev.org/openstack/codegenerator
    $ cd codegenerator
    $ virtualenv .venv
    $ source .venv/bin/activate
    $ pip install -e .

Once installed, you can use the ``openstack-codegenerator`` for all operations.
The ``openstack-codegenerator`` provides a number of *targets*. These
correspond to the various steps required to get a functioning OpenAPI schema.
The first target is the ``openapi-spec`` target. This will generate an initial
OpenAPI schema through inspection of the chosen projects code and api-ref
documentation.

Let's generate an OpenAPI schema for the Compute service, Nova. To do this, we
first need to install Nova in the same virtualenv that we have installed
CodeGenerator in. Let's pull the Nova repo down locally and install it:

.. code-block:: shell

    $ cd ..
    $ git clone https://opendev.org/openstack/nova
    $ cd -
    $ pip install \
        -c https://releases.openstack.org/constraints/upper/master
        -r ../nova/requirements.txt
    $ pip install -e ../nova

With Nova installed, we can now run ``openstack-codegenerator``:

.. code-block:: shell

    $ openstack-codegenerator \
        --work-dir wrk --target openapi-spec --service-type compute \
        --validate

If you look in the path indicated by the ``--work-dir`` argument, you will find
a OpenAPI schema! However, this schema is rather incomplete. That's because
we inspected the Nova code but not the api-ref docs. To do that, we need to
pass a path to our docs, which means we need to build the docs locally. Let's
do this:

.. code-block:: shell

    $ cd ../nova
    $ tox -e api-ref

.. note::

    The ``api-ref`` target *should* be consistent across projects. However,
    it's not currently part of the `Project Testing Interface`__ so this isn't
    guaranteed. If you find this target doesn't exist, look at your project's
    ``tox.ini`` file for clues.

    .. __: https://governance.openstack.org/tc/reference/project-testing-interface.html

You should now have the documentation built in HTML format and available in the
``api-ref/build/html`` directory. Let's change back to the ``codegenerator``
directory and run ``openstack-codegenerator`` again, this time with an
additional ``--api-ref-src`` argument:

.. code-block:: shell

    $ cde ../code-generator
    $ openstack-codegenerator \
        --work-dir wrk --target openapi-spec --service-type compute \
        --api-ref-src ../nova/api-ref/build/html/index.html
        --validate

Your API documentation should now be looking much better. You'll even have
documentation available inline.

There are a variety of options available, which you can view with the
``--help`` option.

.. todo: Expand on other targets, options.
