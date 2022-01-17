Rental Pricelist
====================================================

*This file has been generated on 2021-10-25-10-18-19. Changes to it will be overwritten.*

Summary
-------

Enables the user to define different rental prices with time uom ("Month", "Day" and "Hour").

Description
-----------

Rental prices are usually scaled prices based on a time unit, typically day, sometimes months or hour.
This modules integrates the standard Odoo pricelists into rental use cases and allows the user an
easy way to specify the prices in a product tab as well as to use all the enhanced pricelist features.


Usage
-----

Create a rentable product:
 * Go to Rentals > Configuration > Settings.
 * Please activate the checkbox for using 'Product Variants'.
 * Go to Rentals > Products > Products.
 * Create a new storable product.
 * Active the checkbox 'Can be Rented'.

 Configure the naming of rental services:
 * Go to Settings > Users & Companies > Companies.
 * To to page 'Rental Services'.
 * Configure the rental service names by providing a prefix and suffix for the name and default code.

 Create the rental services:
 * Go to the previously created rentable storable product.
 * Go to page 'Rental Price'.
 * Activate the boolean fields for hourly, daily or monthly rental as needed.
 * Save the product, which creates the related rental services for the given time units.
 * Add a usual price for one hour, one day or one month.
 * Add bulk prices, e.g. one day costs 300 €, 7 days 290 €, 21 days 250 €, and so on.

Hint: The (bulk) prices are added in the product form view of the storable, rentable product
but are actually used for its related rental services!

Create a rental order:
 * Go to Rentals > Customer > Rental Quotations.
 * Create a new order and choose the type 'Rental Order'.
 * Choose the storable rental product (not the rental service!).
 * Choose the rental time unit, which actually loads the correct related rental service.
 * Set the quantity to rent out one or several storable rentable products.
 * Choose start and end date.
 * Confirm the order.
 * Check out the two deliveries, one for outgoing and one for incoming delivery.

Please also see the usage section of sale_rental and rental_base module.


Changelog
---------

- d8665dd9 2021-10-19 12:26:31 +0200 yweng@elegosoft.com  [IMP] Add Unittest for module rental_check_availability and adjust Unittest of rental_pricelist and rental_pricelist_interval (issue 4436)
- c98f3a27 2021-10-10 18:18:12 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/feature_4448_blp1142_rental_pricelist_v12: addons-rental-vertical remotes/origin/feature_4448_blp1142_rental_pricelist_v12 - 04838da6267547849c4cc4a3ecdd8aa7da0fc74f [IMP] make rental service active again after deactiving them , (issue#4448)
- 04838da6 2021-09-28 09:11:35 +0200 cpatel@elegosoft.com  (origin/feature_4448_blp1142_rental_pricelist_v12) [IMP] make rental service active again after deactiving them , (issue#4448)
- 8b4d40c4 2021-09-23 09:19:24 +0200 wagner@elegosoft.com  regenerate doc (issue #4016)
- 46c8af62 2021-09-22 15:37:56 +0200 maria.sparenberg@elegosoft.com  issue #4433 format stuff, add help texts and update usage section
- ad7e8fb7 2021-09-21 16:50:25 +0200 maria.sparenberg@elegosoft.com  issue #4433 add product menu to rental_base, remove configs and dashboard to separate modules
- cef8bcb6 2021-06-25 15:21:15 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/feature_4273_blp1110_rental_product_pack_v12: addons-rental-vertical remotes/origin/feature_4273_blp1110_rental_product_pack_v12 - 8b3f8264d894702df1b16242fefa3f48425f7f43 [IMP] improve german translation,to rental_contract (issue#3920)
- 89ed6dbf 2021-06-25 10:53:08 +0200 cpatel@elegosoft.com  [IMP] display_product_id only to sale.order.line tree view, (issue#4276)
- 317e013f 2021-06-23 14:16:25 +0200 cpatel@elegosoft.com  [IMP]show the display_product_id in sale order line tree view, only for rental lines, (issue#4276)
- dd988a2f 2021-06-09 12:42:47 +0200 wagner@elegosoft.com  update documentation (issue #3613)
- c8a57b35 2021-05-18 17:17:23 +0200 yweng@elegosoft.com  (origin/feature_4222_blp654_update_rental_service_products_v12) [IMP] add option 'translate' in fields prefix und suffix for rental service
- 0cb2ef26 2021-05-04 14:57:25 +0200 yweng@elegosoft.com  (origin/feature_4222_blp635_update_rental_service_products_v12) [IMP] adjust unittest rental tour and fixes the default value of name prefix fields.
- bb4d2f7c 2021-05-03 11:57:13 +0200 yweng@elegosoft.com  [IMP] add update_fields (categ_id, rental, active) for updating fields of rental service (issue 3901)
- 7070c039 2021-04-30 19:43:52 +0200 yweng@elegosoft.com  (origin/feature_4222_blp631_update_rental_service_products_v12, feature_4222_blp631_update_rental_service_products_v12, feature_4222_blp622_update_rental_service_products_v12) [IMP] add function to set prefix and suffix of field name and default_code of rental services
- 84a4d154 2021-04-28 02:18:56 +0200 yweng@elegosoft.com  [IMP] Update fields name, description_sale and image_medium of rental service products after changing of the stockable rental product
- 8dcfb900 2021-04-20 14:48:46 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/v12: addons-rental-vertical remotes/origin/v12 - d1773a45efc72f8191f45e782d492e3f2624a9a5 rental-vertical one time integration of rental-vertical branches by swrent_daily_build-1050
- eac35aea 2021-03-30 09:03:22 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/feature_4110_blp564_refactoring_rental_pricelist_interval_v12: addons-rental-vertical remotes/origin/feature_4110_blp564_refactoring_rental_pricelist_interval_v12 - 0d3a2e4922b5374bb90bf9e835b2addc1eb92dba [IMP] Interval Pricelist
- 0cc27ac8 2021-03-28 21:45:23 +0200 yweng@elegosoft.com  (origin/feature_4046_blp564_rental_check_availability_v12) [ADD] Module rental_check_availability (issue 4046)
- 0d3a2e49 2021-03-26 14:47:41 +0100 yweng@elegosoft.com  (origin/feature_4110_blp564_refactoring_rental_pricelist_interval_v12, feature_4110_blp564_refactoring_rental_pricelist_interval_v12) [IMP] Interval Pricelist
- caacd225 2021-03-26 17:02:17 +0100 cpatel@elegosoft.com  (origin/feature_3901_blp1043_rental_pricelist_v12) [IMP] defaul code changes, (issue#3901)
- b111b867 2021-03-26 13:37:08 +0100 cpatel@elegosoft.com  [IMP] update related rental services if default code of the rental product changes, (issue#3901)
- 3a044991 2021-03-19 00:12:08 +0100 yweng@elegosoft.com  (origin/feature_4110_blp1034_refactoring_rental_pricelist_interval_v12, feature_4110_blp1034_refactoring_rental_pricelist_interval_v12) [IMP] Refactoring of Module rental_pricelist_interval (issue 4110)
- 37ef0a3f 2021-01-27 22:48:39 +0100 yweng@elegosoft.com  (origin/defect_4075_blp969_rental_pricelist_v12) [FIX] function _update_rental_service_analytic_account (issue 4075)
- bbd5cb25 2021-01-14 13:55:22 +0100 wagner@elegosoft.com  adapt gen-doc and update (issue #3613)
- a35a62d4 2020-12-22 22:59:30 +0100 kay.haeusler@elego.de  regenerate all de.po and \*.pot files; issue #4016
- 83ed8f72 2020-12-22 18:06:08 +0100 wagner@elegosoft.com  all Python code reformatted by black code formatter (issue #4016)
- c7e3b592 2020-11-06 09:59:46 +0100 wagner@elegosoft.com  regenerate doc from manifests (issue #3613)
- 391ef2af 2020-10-28 20:59:58 +0100 wagner@elegosoft.com  add usage information for product sets and product packs; add configuration and usage information for rental_sale and extend gen-doc for configuration (issue #3613)
- d39f57e8 2020-10-28 20:18:47 +0100 wagner@elegosoft.com  add links to the index in README.md (issue #3613)
- b1039c8c 2020-10-28 17:39:27 +0100 wagner@elegosoft.com  add index generation and add index to README.md (issue #3613)
- 363cb502 2020-10-28 16:59:43 +0100 wagner@elegosoft.com  change quotes in manifests of rental_forward_shipment_plan and rental_routing and add some draft information about routing; regenerate (issue #3613)
- fb94de5c 2020-10-28 16:20:59 +0100 wagner@elegosoft.com  add descriptions to rental_timeline modules and regenerate (issue #3613)
- f1affe52 2020-10-28 12:45:28 +0100 wagner@elegosoft.com  regenerate doc (issue #3613)
- 86e7c1a6 2020-10-28 12:35:56 +0100 maria.sparenberg@elegosoft.com  issue #3613 add manifest description and usage for several rental modules
- 5244748e 2020-10-27 14:52:26 +0100 wagner@elegosoft.com  regenerate documentation and add README.rst files (issue #3339)
- d02ea5d8 2020-10-27 14:41:06 +0100 wagner@elegosoft.com  (tag: bp_rental_v12_integration-cep-849) update doc generation script (issue #3339)
- b7dad089 2020-10-06 13:48:11 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/fix_3884_blp819_fix_application_status_and_deps_v12: addons-rental-vertical remotes/origin/fix_3884_blp819_fix_application_status_and_deps_v12 - 7580ae8936652f96fb11ac212867967458a4e127 set application to false for all modules except rental_base (issue #3884, issue #3339)
- 836a14b4 2020-10-06 15:33:55 +0200 maria.sparenberg@elegosoft.com  (origin/feature_3477_blp819_rental_product_insurance_v12) issue #3884 rename product_id to insurance_product_id for insurances on sale order lines
- 7580ae89 2020-10-05 22:19:25 +0200 wagner@elegosoft.com  (origin/fix_3884_blp819_fix_application_status_and_deps_v12, fix_3884_blp819_fix_application_status_and_deps_v12) set application to false for all modules except rental_base (issue #3884, issue #3339)
- 1be4b54c 2020-09-15 12:08:18 +0200 yweng@elegosoft.com  (origin/feature_3866_blp804_rename_sale_rental_v12) [MIG] Rename Module sale_rental and rental_sale (update dependence and xml_id)
- 114c04ca 2020-09-11 15:36:33 +0200 yweng@elegosoft.com  (origin/feature_3822_blp790_duplicated_fields_v12) [MIG] Model 'product.template': replace rental_ok with rental
- 3e884f88 2020-08-25 12:20:33 +0200 yweng@elegosoft.com  (origin/feature_3826_blp753_check_rental_order_line_v12) [IMP] add funtions to check the rental order line before Confirm of the Order
- 96567742 2020-08-24 10:30:24 +0200 yweng@elegosoft.com  (origin/feature_3795_blp740_search_product_in_rental_order_v12) [IMP] improves searching on field display_product_id in search view of sale.order
- 1f1c56bc 2020-08-07 18:20:49 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/defect_3782_blp721_contract_date_start_end_v12: addons-rental-vertical remotes/origin/defect_3782_blp721_contract_date_start_end_v12 - df1d31f48e3af1b19c358847178bb19dca77dcbb [FIX] adjust date_start and date_end of sale.order.line for contract
- df1d31f4 2020-08-04 20:30:01 +0200 yweng@elegosoft.com  (origin/defect_3782_blp721_contract_date_start_end_v12) [FIX] adjust date_start and date_end of sale.order.line for contract
- 5e92913a 2020-08-04 11:41:38 +0200 yweng@elegosoft.com  [FIX] warning message for no enough quantity for rental
- 3f9eb75c 2020-07-28 09:54:28 +0200 cpatel@elegosoft.com  (origin/fix_3785_blp712_sol_add_section_note_v12) [FIX] fix on add section/note on sale order line,issue#3785
- eee2472b 2020-06-26 19:24:51 +0200 wagner@elegosoft.com  (origin/fix_3339_blp669_extend_documentation_v12, origin/fix_3339_blp666_extend_documentation_v12, fix_3339_blp669_extend_documentation_v12, fix_3339_blp666_extend_documentation_v12) update documentation (issue #3339)
- 7fcb7460 2020-06-26 11:50:09 +0200 yweng@elegosoft.com  [IMP] adjust function _get_product_domain to sell normal service (without rental service) in rental order (issue 3729)
- e52be419 2020-06-24 12:33:36 +0200 yweng@elegosoft.com  (origin/defect_3729_blp662_sell_service_in_rental_order_v12) [IMP] adjust function _get_product_domain to sell normal service in rental order (issue 3729)
- d244988c 2020-06-10 17:32:49 +0200 yweng@elegosoft.com  [IMP] set invisible for field instance_serial_number_id and Pricelist Items before creating the product
- 57b29fa1 2020-05-24 12:58:49 +0200 wagner@elegosoft.com  (origin/fix_3339_blp622_extend_documentation_v12, origin/fix_3339_bl616_extend_documentation_v12, fix_3339_blp622_extend_documentation_v12, fix_3339_bl616_extend_documentation_v12) update documentation for fix release (issue #3339)
- 3266c20a 2020-05-22 13:33:18 +0200 yweng@elegosoft.com  (origin/defect_3627_blp612_update_analytic_account_v12) [FIX] corrects function _update_rental_service_analytic_account()
- 94dc79ca 2020-05-16 18:10:44 +0200 wagner@elegosoft.com  (origin/fix_3339_blp559_extend_documentation_v12, fix_3339_blp559_extend_documentation_v12) update module documentation (issue #3339)
- 89adaaf3 2020-05-16 14:54:03 +0200 wagner@elegosoft.com  fixup categories and regenerate documentation (issue #3339)
- 134218b1 2020-05-03 18:34:51 +0200 wagner@elegosoft.com  (origin/feature_3339_blp541_update_doc_v12, feature_3339_blp541_update_doc_v12) unify license and author and regenerate documentation (issue #3613, issue #3339)
- 6f03cfa0 2020-04-30 13:20:49 +0200 cpatel@elegosoft.com  (origin/feature_3589_blp521_rental_pricelist_v12) [IMP] rental_pricelist : stop update of start_date,end_date while changing UOM, issue#3589
- 795b1b6a 2020-04-24 20:58:26 +0200 wagner@elegosoft.com  (tag: bp_rental_v12_integration-cep-521, tag: bp_rental_v12_integration-cep-520, tag: bp_rental_v12_integration-cep-519, tag: bp_rental_v12_integration-cep-518, tag: bp_rental_v12_integration-cep-517, tag: bp_rental_v12_integration-cep-516, tag: bp_rental_v12_integration-cep-514, tag: bp_rental_v12_integration-cep-513, tag: bp_rental_v12_integration-cep-512, tag: bp_rental_v12_integration-cep-511, tag: bp_rental_v12_integration-cep-510, tag: bp_rental_v12_integration-cep-509, tag: bp_rental_v12_integration-cep-508, tag: bp_rental_v12_integration-cep-507, tag: bp_rental_v12_integration-cep-506, tag: bp_rental_v12_integration-cep-505, tag: bp_humanilog_v12_integration-cep-322, tag: bp_humanilog_v12_integration-cep-321, tag: bp_humanilog_v12_integration-cep-320, tag: baseline_rental-vertical_v12_swrent_daily_build-503, origin/rental_v12_integration-cep-503, rental_v12_integration-cep-503) regenerate documentation (issue #3613)
- 7fac932a 2020-04-13 14:13:09 +0200 wagner@elegosoft.com  (origin/fix_3339_blp455_extend_documentation_v12, fix_3339_blp455_extend_documentation_v12) regenerate documentation (issue #3339)
- 2da340dc 2020-04-13 14:11:24 +0200 wagner@elegosoft.com  change license for rental-vertical to AGPL (issue #3339)
- 6d3410b3 2020-04-13 13:28:20 +0200 wagner@elegosoft.com  regenerate documentation (issue #3339)
- 0bab92d2 2020-04-09 12:41:12 +0200 wagner@elegosoft.com  (origin/fix_3339_blp355_extend_documentation_v12, fix_3339_blp355_extend_documentation_v12) update/regenerate addon documentation (issue #3339)
- eff3bc08 2020-04-02 13:01:43 +0200 cpatel@elegosoft.com  (origin/feature_3467_blp420_rental_todo_points_v12) [IMP] set start ,end date on sale order line automatically
- ff31876b 2020-03-30 17:55:07 +0200 cpatel@elegosoft.com  [IMP] renatl_contract,rental_pricelist todo points(ticket#3467,ticket#3589) 1. ticket#3467, set the code of automatically created contracts from sale order to the sale order number if the contract subtype has no sequence 2. ticket#3589, The computation of number_of_time_unit is not correct when using the uom Month(s)
- ae995083 2020-03-18 11:50:27 +0100 maria.sparenberg@elegosoft.com  issue #3589 move fields to correct groups in module rental_pricelist
- 3119cfd8 2020-03-18 10:07:48 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/fix_3339_blp384_extend_documentation_v12: addons-rental-vertical remotes/origin/fix_3339_blp384_extend_documentation_v12 - b49c01dabbc653a42b77f82bd3c44a8759721359 regenerate doc (issue #3339)
- c71ec77e 2020-03-18 10:31:23 +0100 yweng@elegosoft.com  (origin/feature_3576_blp384_unittest_instance_appointment_v12) [IMP] delete debug functions in unittests
- fa3d6325 2020-03-18 02:13:25 +0100 yweng@elegosoft.com  [IMP] unittests for module rental_pricelist
- 18339950 2020-03-18 02:12:39 +0100 yweng@elegosoft.com  [FIX] onchange events
- a8e33851 2020-03-16 22:30:45 +0100 yweng@elegosoft.com  [IMP] move product_uom_month from rental_pricelist into rental_base
- b49c01da 2020-03-15 10:12:53 +0100 wagner@elegosoft.com  (origin/fix_3339_blp384_extend_documentation_v12) regenerate doc (issue #3339)
- cea0e942 2020-03-13 20:38:19 +0100 wagner@elegosoft.com  update documentation to build 380 (issue #3339)
- 804dc443 2020-03-07 21:06:12 +0100 wagner@elegosoft.com  regenerate module documentation (issue #3339)
- 6fd1771a 2020-03-06 20:32:25 +0100 kay.haeusler@elego.de  (origin/feature_3462_blp333_renaming_addons_v12) rename and split some addons; issue #3462

