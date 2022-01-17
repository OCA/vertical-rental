Rental Base
====================================================

*This file has been generated on 2021-10-25-10-18-19. Changes to it will be overwritten.*

Summary
-------

Manage Rental of Products

Description
-----------

Base Module for Rental Management

This module provides a new menu for rental management.
It is based on the sale_rental module that currently can be found in sale-workflow repository.


Usage
-----

Create a rentable product and its rental service.
 * Go to Rentals > Configuration > Settings.
 * Please activate the checkbox for using 'Product Variants'.
 * Go to Rentals > Products > Products.
 * Create a new storable product.
 * Activate the checkbox 'Can be Rented'.
 * Go to page 'Sales & Purchase'.
 * Create the rental service and configure its name and price.

Create a rental order:
 * Go to Rentals > Customer > Rental Quotations.
 * Create a new order and choose the type 'Rental Order'.
 * Add the rental service as an order line.
 * Set the quantity to rent out one or several storable rentable products.
 * Choose start and end date.
 * Confirm the order.
 * Check out the two deliveries, one for outgoing and one for incoming delivery.

Please also see the usage section of sale_rental module.


Changelog
---------

- d32f4bf1 2021-10-19 13:27:01 +0200 maria.sparenberg@elegosoft.com  issue #4439 format code and finalize description and usage section
- bc386fa1 2021-10-10 18:18:14 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/fix_3339_blp1142_update_start_end_date_v12: addons-rental-vertical remotes/origin/fix_3339_blp1142_update_start_end_date_v12 - 2906b713c7dbf38b2bf5da09627dd51dd0198cbe [FIX] function update_start_end_date() of sale.order.line (issue 3339)
- 75791881 2021-09-24 08:44:15 +0200 maria.sparenberg@elegosoft.com  (origin/feature_4433_blp1142_rental_base_v12, feature_4433_blp1142_rental_base_v12) issue #4433 change view id to match parent id
- 8b4d40c4 2021-09-23 09:19:24 +0200 wagner@elegosoft.com  regenerate doc (issue #4016)
- ad7e8fb7 2021-09-21 16:50:25 +0200 maria.sparenberg@elegosoft.com  issue #4433 add product menu to rental_base, remove configs and dashboard to separate modules
- 2906b713 2021-08-03 16:16:44 +0200 yweng@elegosoft.com  (origin/fix_3339_blp1142_update_start_end_date_v12, fix_3339_blp1142_update_start_end_date_v12) [FIX] function update_start_end_date() of sale.order.line (issue 3339)
- 6ba4bcb9 2021-07-01 16:33:45 +0200 yweng@elegosoft.com  [IMP] implements Unittest for module rental_routing and rental_forward_shipment_plan
- dd988a2f 2021-06-09 12:42:47 +0200 wagner@elegosoft.com  update documentation (issue #3613)
- 1abc79fe 2021-05-12 18:08:04 +0200 yweng@elegosoft.com  (origin/wip_4168_sale_rental_v12, wip_4168_sale_rental_v12) [IMP] adjust dependence of rental modules: replace rental_sale with sale_rental
- 27e3d7c6 2021-02-16 20:03:33 +0100 yweng@elegosoft.com  (origin/feature_4045_blp997_update_sale_line_date_v12) [IMP] improve wizard update.sale.line.date to add message with origin date (issue 4101)
- 4b79005a 2021-02-10 20:06:51 +0100 yweng@elegosoft.com  (origin/feature_4045_blp993_update_sale_line_date_v12) [IMP] improves wizard update.sale.line.date (issue 4045)
- 976ad0c2 2021-01-20 14:08:02 +0100 yweng@elegosoft.com  (origin/feature_3966_blp969_rental_base_v12) [IMP] change the name of menu back (issue 4048)
- f42ce87b 2021-01-19 17:03:34 +0100 yweng@elegosoft.com  [IMP] Refactoring of module rental_base (issue 4048)
- a9665a4d 2020-11-26 21:13:46 +0100 yweng@elegosoft.com  [IMP] remove some depends of rental_base
- bbd5cb25 2021-01-14 13:55:22 +0100 wagner@elegosoft.com  adapt gen-doc and update (issue #3613)
- a35a62d4 2020-12-22 22:59:30 +0100 kay.haeusler@elego.de  regenerate all de.po and \*.pot files; issue #4016
- 83ed8f72 2020-12-22 18:06:08 +0100 wagner@elegosoft.com  all Python code reformatted by black code formatter (issue #4016)
- 32ebf049 2020-12-17 14:01:20 +0100 yweng@elegosoft.com  (origin/defect_3953_blp925_update_date_in_sale_order_line_v12) [FIX] update_start_end_date() of sale.order.line to update the start_date later (issue 3953)
- 8101749b 2020-11-25 13:13:07 +0100 yweng@elegosoft.com  (origin/defect_3722_blp862_rental_timeline_product_instance_v12) [IMP] fixes conflict between sale_order_revision and sale_order_type
- 1b3f4854 2020-11-07 19:21:05 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/feature_3339_blp849_rental_icon_v12: addons-rental-vertical remotes/origin/feature_3339_blp849_rental_icon_v12 - 89aa2125126c4a3599bd6c3e58ff0a788bf8019d issue #3339 change rental icon (not perfect yet but better)
- c7e3b592 2020-11-06 09:59:46 +0100 wagner@elegosoft.com  regenerate doc from manifests (issue #3613)
- 89aa2125 2020-11-05 13:40:17 +0100 maria.sparenberg@elegosoft.com  (origin/feature_3339_blp849_rental_icon_v12) issue #3339 change rental icon (not perfect yet but better)
- 391ef2af 2020-10-28 20:59:58 +0100 wagner@elegosoft.com  add usage information for product sets and product packs; add configuration and usage information for rental_sale and extend gen-doc for configuration (issue #3613)
- d39f57e8 2020-10-28 20:18:47 +0100 wagner@elegosoft.com  add links to the index in README.md (issue #3613)
- b1039c8c 2020-10-28 17:39:27 +0100 wagner@elegosoft.com  add index generation and add index to README.md (issue #3613)
- 363cb502 2020-10-28 16:59:43 +0100 wagner@elegosoft.com  change quotes in manifests of rental_forward_shipment_plan and rental_routing and add some draft information about routing; regenerate (issue #3613)
- fb94de5c 2020-10-28 16:20:59 +0100 wagner@elegosoft.com  add descriptions to rental_timeline modules and regenerate (issue #3613)
- f1affe52 2020-10-28 12:45:28 +0100 wagner@elegosoft.com  regenerate doc (issue #3613)
- 5244748e 2020-10-27 14:52:26 +0100 wagner@elegosoft.com  regenerate documentation and add README.rst files (issue #3339)
- d02ea5d8 2020-10-27 14:41:06 +0100 wagner@elegosoft.com  (tag: bp_rental_v12_integration-cep-849) update doc generation script (issue #3339)
- 836a14b4 2020-10-06 15:33:55 +0200 maria.sparenberg@elegosoft.com  (origin/feature_3477_blp819_rental_product_insurance_v12) issue #3884 rename product_id to insurance_product_id for insurances on sale order lines
- b4743f79 2020-10-05 16:13:02 +0200 maria.sparenberg@elegosoft.com  (origin/defect_3880_blp819_timeline_confirmed_so_v12) issue #3880 allow updating confirmed order lines and corresponding timeline entries and contract lines
- 7614f12d 2020-10-05 11:36:43 +0200 maria.sparenberg@elegosoft.com  issue #3880 allow creation of new order lines with start and end date in order state 'sale'
- 1be4b54c 2020-09-15 12:08:18 +0200 yweng@elegosoft.com  (origin/feature_3866_blp804_rename_sale_rental_v12) [MIG] Rename Module sale_rental and rental_sale (update dependence and xml_id)
- 3583d36b 2020-09-10 12:51:56 +0200 cpatel@elegosoft.com  (origin/fix_3785_blp778_rental_base_v12) [IMP] rental_base module:small correction,set max to end_date
- 46fc1945 2020-09-09 16:23:11 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/fix_3785_blp776_sol_add_section_note_v12: addons-rental-vertical remotes/origin/fix_3785_blp776_sol_add_section_note_v12 - 5b6bde7e843f5aafbcdd009f46989c2966901118 [FIX] made fix to rental_base,when you add section line or note in sale order line,issue#3785
- fd924f15 2020-09-09 11:41:46 +0200 maria.sparenberg@elegosoft.com  (origin/feature_3824_blp776_rental_repair_v12) issue #3824 fix German translation
- 5b6bde7e 2020-09-09 11:40:49 +0200 cpatel@elegosoft.com  (origin/fix_3785_blp776_sol_add_section_note_v12) [FIX] made fix to rental_base,when you add section line or note in sale order line,issue#3785
- 470ce252 2020-09-08 14:39:38 +0200 yweng@elegosoft.com  (origin/feature_3477_blp776_rental_product_insurance_v12) [IMP] corrects some translations (issue 3766)
- eb33ba5d 2020-09-07 18:19:32 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/fix_3627_blp753_rental_config_menu_group_v12: addons-rental-vertical remotes/origin/fix_3627_blp753_rental_config_menu_group_v12 - 09ac7b8c8b810851b2792b6ce2c3ccf397980042 [IMP] add group to Rental/Config menu, to avoid error when click everywhere will run,issue#3627
- 74abd2c7 2020-09-02 13:27:59 +0200 yweng@elegosoft.com  (origin/feature_3766_blp753_rental_partner_contract_smartbutton_v12) [IMP] adjust Menus for contracts
- 09ac7b8c 2020-09-02 12:39:59 +0200 cpatel@elegosoft.com  (origin/fix_3627_blp753_rental_config_menu_group_v12) [IMP] add group to Rental/Config menu, to avoid error when click everywhere will run,issue#3627
- 1f1c56bc 2020-08-07 18:20:49 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/defect_3782_blp721_contract_date_start_end_v12: addons-rental-vertical remotes/origin/defect_3782_blp721_contract_date_start_end_v12 - df1d31f48e3af1b19c358847178bb19dca77dcbb [FIX] adjust date_start and date_end of sale.order.line for contract
- 89659751 2020-08-07 18:20:47 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/fix_3785_blp721_sol_inv_add_section_note_v12: addons-rental-vertical remotes/origin/fix_3785_blp721_sol_inv_add_section_note_v12 - 64e6d5c21633d21cc5030fddd8d8c9a99062f448 [IMP] improve service period dates compute functions,issue3785
- 64e6d5c2 2020-08-06 18:47:01 +0200 cpatel@elegosoft.com  (origin/fix_3785_blp721_sol_inv_add_section_note_v12) [IMP] improve service period dates compute functions,issue3785
- df1d31f4 2020-08-04 20:30:01 +0200 yweng@elegosoft.com  (origin/defect_3782_blp721_contract_date_start_end_v12) [FIX] adjust date_start and date_end of sale.order.line for contract
- 5d551a02 2020-08-03 18:30:41 +0200 yweng@elegosoft.com  [IMP] adjusts domain of menu action to show quotations and orders for sales/rentals
- 1dc93f57 2020-07-15 13:51:42 +0200 yweng@elegosoft.com  (origin/feature_3752_blp700_view_canceled_rental_order_v12) [IMP] show canceled rental orders in action_rental_orders and action_rental_quotations
- a196d00c 2020-07-13 09:22:09 +0200 yweng@elegosoft.com  (origin/feature_3760_blp695_rental_menu_dashboard_v12) [IMP] add menu dashboard
- 0121f5c5 2020-07-03 11:22:21 +0200 yweng@elegosoft.com  (origin/defect_3751_blp677_delete_rental_order_v12) [IMP] extends unlink function of sale.order to delete the linked sale.rental record at first.
- eee2472b 2020-06-26 19:24:51 +0200 wagner@elegosoft.com  (origin/fix_3339_blp669_extend_documentation_v12, origin/fix_3339_blp666_extend_documentation_v12, fix_3339_blp669_extend_documentation_v12, fix_3339_blp666_extend_documentation_v12) update documentation (issue #3339)
- 57b29fa1 2020-05-24 12:58:49 +0200 wagner@elegosoft.com  (origin/fix_3339_blp622_extend_documentation_v12, origin/fix_3339_bl616_extend_documentation_v12, fix_3339_blp622_extend_documentation_v12, fix_3339_bl616_extend_documentation_v12) update documentation for fix release (issue #3339)
- 3188aa77 2020-05-20 11:15:34 +0200 cpatel@elegosoft.com  (origin/fix_3339_blp602_refactor_menu_view_v12) [FIX] remove ref of mis_builder from rental_base and moved menu items to rental_reporting module
- 94dc79ca 2020-05-16 18:10:44 +0200 wagner@elegosoft.com  (origin/fix_3339_blp559_extend_documentation_v12, fix_3339_blp559_extend_documentation_v12) update module documentation (issue #3339)
- e310d9b9 2020-05-16 13:18:01 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/fix_3339_blp559_remove_dependency_to_product_tweaks_v12: addons-rental-vertical remotes/origin/fix_3339_blp559_remove_dependency_to_product_tweaks_v12 - ad1cfe07746960755671826cfb2a20aa889b5533 remove dependency to third-party addon prt_product_tweaks (issue #3339)
- 89adaaf3 2020-05-16 14:54:03 +0200 wagner@elegosoft.com  fixup categories and regenerate documentation (issue #3339)
- 0a560fd4 2020-05-16 14:49:58 +0200 wagner@elegosoft.com  extract rental reporting menu to rental_reporting (issue #3339)
- c5dbd032 2020-05-16 14:47:55 +0200 wagner@elegosoft.com  remove crm dependency from rental_base (issue #3339)
- 7d232418 2020-05-16 14:20:55 +0200 wagner@elegosoft.com  (re)generate documentation for rental_base and rental_menu_crm (issue #3339)
- 6d22b8d3 2020-05-16 14:19:32 +0200 wagner@elegosoft.com  extract rental CRM menu to rental_menu_crm (issue #3339)
- ad1cfe07 2020-05-16 10:37:51 +0200 wagner@elegosoft.com  (origin/fix_3339_blp559_remove_dependency_to_product_tweaks_v12, fix_3339_blp559_remove_dependency_to_product_tweaks_v12) remove dependency to third-party addon prt_product_tweaks (issue #3339)
- 134218b1 2020-05-03 18:34:51 +0200 wagner@elegosoft.com  (origin/feature_3339_blp541_update_doc_v12, feature_3339_blp541_update_doc_v12) unify license and author and regenerate documentation (issue #3613, issue #3339)
- e5c59af9 2020-05-02 00:38:12 +0200 kay.haeusler@elego.de  (origin/feature_3642_blp531_product_highlights_v12) move the menu products from rental_product_variant to rental_base; issue #3642
- 795b1b6a 2020-04-24 20:58:26 +0200 wagner@elegosoft.com  (tag: bp_rental_v12_integration-cep-521, tag: bp_rental_v12_integration-cep-520, tag: bp_rental_v12_integration-cep-519, tag: bp_rental_v12_integration-cep-518, tag: bp_rental_v12_integration-cep-517, tag: bp_rental_v12_integration-cep-516, tag: bp_rental_v12_integration-cep-514, tag: bp_rental_v12_integration-cep-513, tag: bp_rental_v12_integration-cep-512, tag: bp_rental_v12_integration-cep-511, tag: bp_rental_v12_integration-cep-510, tag: bp_rental_v12_integration-cep-509, tag: bp_rental_v12_integration-cep-508, tag: bp_rental_v12_integration-cep-507, tag: bp_rental_v12_integration-cep-506, tag: bp_rental_v12_integration-cep-505, tag: bp_humanilog_v12_integration-cep-322, tag: bp_humanilog_v12_integration-cep-321, tag: bp_humanilog_v12_integration-cep-320, tag: baseline_rental-vertical_v12_swrent_daily_build-503, origin/rental_v12_integration-cep-503, rental_v12_integration-cep-503) regenerate documentation (issue #3613)
- 7fac932a 2020-04-13 14:13:09 +0200 wagner@elegosoft.com  (origin/fix_3339_blp455_extend_documentation_v12, fix_3339_blp455_extend_documentation_v12) regenerate documentation (issue #3339)
- 2da340dc 2020-04-13 14:11:24 +0200 wagner@elegosoft.com  change license for rental-vertical to AGPL (issue #3339)
- 6d3410b3 2020-04-13 13:28:20 +0200 wagner@elegosoft.com  regenerate documentation (issue #3339)
- 0bab92d2 2020-04-09 12:41:12 +0200 wagner@elegosoft.com  (origin/fix_3339_blp355_extend_documentation_v12, fix_3339_blp355_extend_documentation_v12) update/regenerate addon documentation (issue #3339)
- f1a193ef 2020-03-27 12:29:28 +0100 cpatel@elegosoft.com  (origin/feature_3279_blp420_rental_product_todo_points_v12) [IMP] german translation rental_base,rental_product_instance, ticket#3286
- fc0321b9 2020-03-27 10:50:44 +0100 cpatel@elegosoft.com  [IMP] todo points rental_base and rental_product_instance , ticket#3286
- 94f6f717 2020-03-26 10:09:51 +0100 cpatel@elegosoft.com  [IMP] todo points of rental product , ticket #3279
- 5cd55b28 2020-03-25 19:33:13 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/feature_3593_blp412_rental_product_instance_v12: addons-rental-vertical remotes/origin/feature_3593_blp412_rental_product_instance_v12 - bbea9f1641b460a2b886c32b8f8f066be81bca9a [ADD] module rental_contract_insurance
- 0354a694 2020-03-25 14:28:18 +0100 cpatel@elegosoft.com  (origin/feature_3589_blp412_rental_base_todo_points_v12) [IMP] todo points related to start and end date, ticket #3589
- 07e6c646 2020-03-24 17:06:54 +0100 yweng@elegosoft.com  [IMP] rental_product_insurance
- 197443ee 2020-03-22 16:48:33 +0100 yweng@elegosoft.com  [IMP] improves form-, tree- and search-view of products (issue 3593)
- 589487ac 2020-03-21 12:21:30 +0100 maria.sparenberg@elegosoft.com  issue #3589 move some fields in sale order form for rental orders
- 823d4c78 2020-03-17 20:06:15 +0100 maria.sparenberg@elegosoft.com  issue #3589 improve sale order (line) view in rental_base module
- 3119cfd8 2020-03-18 10:07:48 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/fix_3339_blp384_extend_documentation_v12: addons-rental-vertical remotes/origin/fix_3339_blp384_extend_documentation_v12 - b49c01dabbc653a42b77f82bd3c44a8759721359 regenerate doc (issue #3339)
- c71ec77e 2020-03-18 10:31:23 +0100 yweng@elegosoft.com  (origin/feature_3576_blp384_unittest_instance_appointment_v12) [IMP] delete debug functions in unittests
- fa3d6325 2020-03-18 02:13:25 +0100 yweng@elegosoft.com  [IMP] unittests for module rental_pricelist
- 59734977 2020-03-17 11:39:36 +0100 yweng@elegosoft.com  [MIG] add migration script for module rental_base 12.0.1.0.1
- a8e33851 2020-03-16 22:30:45 +0100 yweng@elegosoft.com  [IMP] move product_uom_month from rental_pricelist into rental_base
- b49c01da 2020-03-15 10:12:53 +0100 wagner@elegosoft.com  (origin/fix_3339_blp384_extend_documentation_v12) regenerate doc (issue #3339)
- cea0e942 2020-03-13 20:38:19 +0100 wagner@elegosoft.com  update documentation to build 380 (issue #3339)
- c9f5b81f 2020-03-13 08:48:23 +0100 maria.sparenberg@elegosoft.com  (origin/feature_3467_blp371_rentals_menu_v12) issue #3467 fix menu strings and translation
- 705a1979 2020-03-12 23:49:11 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/feature_3576_blp355_rental_product_pack_v12: addons-rental-vertical remotes/origin/feature_3576_blp355_rental_product_pack_v12 - b367d1778430938c768f5ab84bd8e543f34f113f [IMP] Unittests of module rental_product_instance
- b367d177 2020-03-11 22:02:43 +0100 yweng@elegosoft.com  (origin/feature_3576_blp355_rental_product_pack_v12) [IMP] Unittests of module rental_product_instance
- a5b57990 2020-03-11 17:48:38 +0100 yweng@elegosoft.com  [IMP] Unittests of module rental_product_pack
- b215fe38 2020-03-11 14:35:38 +0100 maria.sparenberg@elegosoft.com  (origin/feature_3462_blp355_menu_translation_v12) issue #3462 change German translation for purchase order
- 804dc443 2020-03-07 21:06:12 +0100 wagner@elegosoft.com  regenerate module documentation (issue #3339)
- 6fd1771a 2020-03-06 20:32:25 +0100 kay.haeusler@elego.de  (origin/feature_3462_blp333_renaming_addons_v12) rename and split some addons; issue #3462
- 20d0a8d5 2020-03-05 23:04:10 +0100 kay.haeusler@elego.de  (origin/feature_3287_blp326_fix_strings_translation_manifest_v12) Rename 'Repair Orders' to 'Repair Quotations'; issue #3462
- fc3b3089 2020-03-05 16:12:50 +0100 maria.sparenberg@elegosoft.com  issue #3287 fix description and help texts, add German translation
- 4c76ef2b 2020-03-04 16:56:16 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/fix_3339_blp311_extend_documentation_v12: addons-rental-vertical remotes/origin/fix_3339_blp311_extend_documentation_v12 - 7dde7fa1ec109919795e59198feb24fc96fcfeb1 add changelogs in HISTORY.rst and some minor improvements (issue #3339)
- e0caf88d 2020-03-04 16:56:14 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/fix_3287_blp311_sale_rental_pricelist_v12: addons-rental-vertical remotes/origin/fix_3287_blp311_sale_rental_pricelist_v12 - 23c09f7decb00e1fcbf5f8b7fadb28f425442848 [IMP] add config option of model_rental_product_instance_appointment
- 8d65c409 2020-03-04 16:56:06 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/feature_3462_blp311_refactoring_menus_v12: addons-rental-vertical remotes/origin/feature_3462_blp311_refactoring_menus_v12 - 6bcb6e6f14bb87e546b372f83f6f0b6961e60c71 Menu refactoring; issue #3462
- 23c09f7d 2020-03-04 12:53:13 +0100 yweng@elegosoft.com  (origin/fix_3287_blp311_sale_rental_pricelist_v12) [IMP] add config option of model_rental_product_instance_appointment
- 6bcb6e6f 2020-03-03 16:57:04 +0100 kay.haeusler@elego.de  (origin/feature_3462_blp311_refactoring_menus_v12) Menu refactoring; issue #3462
- 7dde7fa1 2020-03-03 00:19:35 +0100 wagner@elegosoft.com  (origin/fix_3339_blp311_extend_documentation_v12, fix_3339_blp311_extend_documentation_v12) add changelogs in HISTORY.rst and some minor improvements (issue #3339)
- 45c5c329 2020-03-02 09:35:59 +0100 cpatel@elegosoft.com  (origin/feature_3306_blp311_config_setting_import_invoice_v12) [IMP] remove invoice imort config setting from Rental-Configuration-Settings menu
- e40e7db1 2020-03-01 14:54:48 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/feature_3339_blp297_add_some_module_descriptions_v12: addons-rental-vertical remotes/origin/feature_3339_blp297_add_some_module_descriptions_v12 - 467665c9235e57ea2552ec037f6561e8f18a9b8d add some generated reST and HTML documentation (issue #3339)
- 467665c9 2020-03-01 15:50:45 +0100 wagner@elegosoft.com  (origin/feature_3339_blp297_add_some_module_descriptions_v12, feature_3339_blp297_add_some_module_descriptions_v12) add some generated reST and HTML documentation (issue #3339)
- 6965ed1c 2020-02-29 22:46:34 +0100 wagner@elegosoft.com  fix some mistakes in author and license, make summaries one line, add some descriptions (issue #3339)
- a86d641a 2020-02-26 15:11:02 +0100 cpatel@elegosoft.com  (origin/feature_3306_blp297_config_setting_import_invoice_v12) [IMP] config setting for import invoice
- 50d383ad 2020-02-19 14:59:04 +0100 kay.haeusler@elego.de  reorder and create new rental menu items; issue #3462
- 46f26e7c 2020-02-13 10:22:44 +0100 kay.haeusler@elego.de  (origin/feature_3279_blp239_refactoring_menus_v12) add missing dependency; issue #3279
- a88dfb52 2020-02-12 12:57:10 +0100 yweng@elegosoft.com  [IMP] refactoring of menus
- 9a555c74 2020-02-10 19:52:46 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/feature_3304_blp214_german_translation_v12: addons-rental-vertical remotes/origin/feature_3304_blp214_german_translation_v12 - 94d9308ebc1357bfaee0061925fd5d59cdd50ccd issue #3304 add German translation for rental_base module
- 94d9308e 2020-02-10 16:25:21 +0100 maria.sparenberg@elegosoft.com  (origin/feature_3304_blp214_german_translation_v12) issue #3304 add German translation for rental_base module
- de769196 2020-02-10 14:00:04 +0100 yweng@elegosoft.com  [IMP] auto setting analytic account by creating invoice and creating rental server product
- bf0ec647 2020-02-04 15:36:13 +0100 yweng@elegosoft.com  (origin/feature_3287_blp198_rental_sale_offday_v12) [ADD] add module rental_sale_offday
- 2f11b55a 2020-01-29 17:46:18 +0100 yweng@elegosoft.com  [IMP] improves form view of products
- 545a3adf 2020-01-28 13:24:17 +0100 yweng@elegosoft.com  [IMP] refactoring of project_task_order, functions is moved into rental_product_instance_repair and rental_repair.
- 91b28636 2020-01-27 18:45:23 +0100 yweng@elegosoft.com  (origin/feature_3467_blp157_rental_contract_v12) [IMP] reset default action (timeline) of root menu
- 6a26f1d4 2020-01-23 22:58:59 +0100 yweng@elegosoft.com  [IMP] add new filter for product search view and adjust the menu of timeline overview
- 73e3d27d 2020-01-23 22:37:27 +0100 yweng@elegosoft.com  [IMP] add context (default_type_id) for menu action of rental order and add dynamic domain on fields product_id of sale.order.line
- 94e76bbb 2020-01-23 13:08:03 +0100 yweng@elegosoft.com  [IMP] set liscense, copyrights and author
- 4aa3ee3c 2020-01-23 12:11:29 +0100 yweng@elegosoft.com  [IMP] change icon of rental_base
- 5188db94 2020-01-22 20:51:43 +0100 yweng@elegosoft.com  [ADD] add module rental_contract
- 7aa3746c 2020-01-22 15:22:34 +0100 cpatel@elegosoft.com  (origin/feature_3304_blp157_rental_base_config_setting_v12) [IMP] add config setting for module rental_product_set
- b2e6d5ce 2020-01-21 20:51:21 +0100 yweng@elegosoft.com  (origin/feature_3304_blp151_refactoring_swrent_product_extension_v12) [IMP] Add neu Module rental_base, rental_product_pack and Refactoring of module sale_rental_menu (deprecated)

