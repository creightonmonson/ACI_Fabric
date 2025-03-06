# ACI Fabric Infrastructure as Code

The goal of this repo is to provide the framework to deploy and maintain an ACI fabric using Ansible, and to do so in a modular fashion. The organization of this repo is don ein a way to maximize scalability and flexibility.

```
Directory Structure:

-ACI_Hosts.yml -----------> Host File for Fabric 1 APIC 
-group_vars
    - all.yml ----------> Contains connection variables
-host_vars    ----------> host vars split into access policies and tenant policies 
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
        o tn-l3out -----------> Variables for L3out 
        o tn-contracts.yml ---> Variables for creating and binding contracts

- playbooks (Organized by Fabric and Logical/Physical model)
    - fabric1  ---------------> Playbooks for Fabric1
        - access_policies
            o fab1-ap.yml  ---> Access Policies playbook for Fabric1
        - tenant_policies
            o fab1-tn.yml  ---> Tenant Policies playbook for Fabric1

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
    o tn_l3out
    o tn_contracts
```

## How to Use
Add to variable files to add any new objects to the access or tenant policies. The goal is to be able to control the entire ACI Fabric through variable files as the variables will be the expected state of the network. Every object (for instance, an EPG) should have a "state" variable, which you will use to control that objects presence in the configuration. This is so that if you want to delete an object down the road, you would change that variable to state = absent and run the playbook which will cause that object to be removed. Note that if you just delete a variable and run the playbook, the object still remains in the configuration. 

The structure of this repo was built so that you can easily add another fabric to this infrastructure by simply creating another host to the host file. The playbook directory "fabric1" could be copied to another directory,say "fabric2" and change the playbook targeted host to fabric2. Alternately, the name of the directory could be changed to say, ACI_MultiSite, and change the playbook target host from Fabric1 to All. 

#### Deploy the initial settings (system settings and fabric policy):

`ansible-playbook playbooks/fabric1/initial_setup/fab1-initial-setup.yml -i ACI_Hosts.yml`

#### Deploy the Access Policies:
`ansible-playbook playbooks/fabric1/access_policies/fab1-ap.yml -i ACI_Hosts.yml`

#### Deploy the Tenant Policies:
`ansible-playbook playbooks/fabric1/tenant_policies/fab1-tn.yml -i ACI_Hosts.yml`

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


