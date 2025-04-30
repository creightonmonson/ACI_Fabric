# ACI Fabric Infrastructure as Code

The goal of this repo is to provide the framework to deploy and maintain an ACI fabric using Ansible, and to do so in a modular fashion. The organization of this repo is done in a way to maximize scalability and flexibility. Each role has an associated variables file in host_vars to increase readability. Access policy variables in the host_vars are commented out currently to test using csv files instead. Also, variables are organized in a way to use Loops as much as possible in the roles/tasks so that additions to the fabric configuration can be accomplished simply by adding new variables to the vars files.

```
Directory Structure:

-ACI_Hosts.yml -----------> Host File for Fabric 1 APIC 
-group_vars
    - all.yml ----------> Contains connection variables
-host_vars    ----------> host vars split into access policies and tenant policies per fabric
    - fabric1
        - access_policies
            o ap-swp.yml ---------> Variables for switch profiles
            o ap-ifp.yml ---------> Variables for interface profiles
            o ap-int-policy.yml --> Variables for Policies (LACP, LLDP, etc)
            o ap-access-ipg.yml --> Variables for access port policy groups (IPG)
            o ap-vpc-ipg.yml -----> Variables for VPC port policy groups
            o ap-vpc-prot-grp ----> Variables for VPC domain protection group
            o ap-interface-selector.yml ---> Variables for interfaces port selector
            o ap-vlanpools.yml ---> Variables for VLAN pools
            o ap-domains.yml -----> Variables for domains
            o ap-aaep.yml --------> Variables for AAEP
        - tenant_policies
            o tn-tenant.yml ------> Variables for creating tenants
            o tn-vrf -------------> Variables for creating VRFs
            o tn-ap  -------------> Variables for creating Application Profiles
            o tn-bd  -------------> Variables for creating Bridge Domains
            o tn-bd-subnets ------> Variables for applying subnets to BDs
            o tn-epg  ------------> Variables for creating endpoint groups
            o tn-esg  ------------> Variables for creating endpoint security groups
            o tn-l3out -----------> Variables for L3out 
            o tn-contracts.yml ---> Variables for creating and binding contracts

- roles  (A Role for each variable file that are then referenced in playbooks)
    o ap_swp
    o ap_ifp
    o ap_int_policy
    o ap_access_ipg
    o ap_vpc_ipg
    o ap_vpc_prot_grp
    o ap_interface_selector
    o ap_vlanpools
    o ap_domains
    o ap_aaep
    o tn_tenant
    o tn_vrf
    o tn_ap
    o tn_bd
    o tn_epg
    o tn_esg
    o tn_l3out
    o tn_contracts
    o initial_setup
    o snapshot
    o fabric_deploy

system_configuration_deploy.yml -------> Playbook to deploy system configurations 
access_policy_deploy.yml  -------------> Playbook to deploy access policies
tenant_policy_deploy.yml  -------------> Playbook to deploy tenant policies
snapshot.yml              -------------> Playbook to take a snapshot
fabric_deploy.yml         -------------> Playbook that runs system, access_policy, and tenant_policy playbooks sequentially
register_nodes.yml        -------------> Playbook to register new nodes to fabric

```

## How to Use
Add to variable files to add any new objects to the access or tenant policies. The goal is to be able to control the entire ACI Fabric through variable files as the variables will be the expected state of the network. Every object (for instance, an EPG) should have a "state" variable, which you will use to control that objects presence in the configuration. This is so that if you want to delete an object down the road, you would change that variable to state = absent and run the playbook which will cause that object to be removed. Note that if you just delete a variable and run the playbook, the object still remains in the configuration. 

The structure of this repo was built so that you can easily add another fabric to this infrastructure by simply creating another host to the host file and then taking all the vars files from host_vars/fabric1 and pasting them into host_vars/fabric2 and setting the variables appropriately for the new fabric. Then change the playbooks host from fabric1 to fabric2, or if you want to configure both fabrics at the same time set the host to mynetwork.

#### Deploy the initial settings (system settings and fabric policy):

`ansible-playbook system_configuration_deploy.yml -i ACI_Hosts.yml`

#### Deploy the Access Policies:
`ansible-playbook access_policy_deploy.yml -i ACI_Hosts.yml`

#### Deploy the Tenant Policies:
`ansible-playbook tenant_policy_deploy.yml -i ACI_Hosts.yml`

#### Deploy Fabric:
This playbook uses ansible import to run the above 3 playbooks in a row to maintain the state of the entire fabric. 

`ansible-playbook fabric_deploy.yml -i ACI_Hosts.yml`

## Notes
Each task has error handling specifically added to avoid timeout errors from the APIC API. I found when running the playbooks that the API would send 503 errors occasionally which caused the playbook to fail.

If you add or modify roles, be sure each task has the following for error handling:
```
delegate_to: localhost       # Without this, Ansible will pass the module to the APIC for the APIC to run the task
register: result                # temporarily store the results of this task
retries: "{{ loop_retries }}"   # retry the task 3 times
delay: "{{ retry_delay }}"      # wait 3 seconds before retrying
until: result.failed == false   # exit the retry loop when task suceeds
```

## Github Actions Workflow
A github actions workflow (pipeline) is located in the .github/workflows directory, and executes the following using a self-hosted runner configured on an ubuntu server:
- Ansible Linting/syntax validation
- Ansible dry-run:

     This job runs the ansible playbook fabric_deploy.yml using check mode. When playbooks are running in check mode, they do not make changes in the infrastructure, instead Ansible just simulates the changes. When using check mode together with Cisco ACI Ansible collection, the body of POST requests is saved in an output file (.json)that can be found in outputs directory. 

- Snapshot:

    This job runs a snapshot in the ACI fabric that can be used as a rollback point 

- Ansible Deployment:

    This job runs the fabric_deploy playbook


Future use of the dry-run output (.json) is to use these with NDI's pre-change analysis to validate the changes. Also will look to add a post-change analysis using NDI's delta analysis. Also, future additions will be to use a docker container for the ansible tasks on the runner. 
