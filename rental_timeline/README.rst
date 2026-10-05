Rental Timeline
====================================================

*This file has been generated on 2022-07-26-13-09-49. Changes to it will be overwritten.*

Summary
-------

Adds a timeline to products as well as a timeline view as overview of all rental products and orders

Description
-----------

This module extends the sale_rental module to create and change the timeline objects
for the rented product instances automatically.
A complete timeline view containing all rental orders will be generated for all rentable products.

This module adds the basic rental timeline view as well as an extension to the product form view.


Usage
-----

Just install this module to add the rental timeline view to your system. No further configuration is necessary.


Changelog
---------

- 3e36d7bd 2022-06-20 16:50:34 +0200 cpatel@elegosoft.com  [IMP] refactor rental modules to isolate fleet and vehicle related fields, (issue#4955)
- 2d6ba4d8 2022-05-23 12:38:59 +0200 cpatel@elegosoft.com  [IMP] refactor the dependencies in rental modules, (issue#4955)
- 1e549e87 2022-05-04 12:56:56 +0200 wagner@elegosoft.com  (origin/feature_2832_blp7_new_logos_v12, feature_2832_blp7_new_logos_v12) update doc (issue #3613, issue #4016)
- 02eb49c8 2022-05-04 12:18:32 +0200 wagner@elegosoft.com  update doc (issue #4016)
- 4ff94cf3 2022-05-04 12:09:50 +0200 wagner@elegosoft.com  add new rental logo (issue #3613, issue #4016)
- 1730e660 2022-04-14 15:09:43 +0200 cpatel@elegosoft.com  (origin/feature_4995_blp1379_refactor_fleet_extensions_v12) [IMP] refactore fleet and vehicle related fields,(issue#4955)
- d2b67af6 2022-01-14 14:17:40 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/feature_4100_blp1295_timeline-group-by-product-categories-or-partners-or-orders_v12: addons-rental-vertical remotes/origin/feature_4100_blp1295_timeline-group-by-product-categories-or-partners-or-orders_v12 - cb5ffd044719126fff8ba785721ff1e048e475ba refactor timeline_renderer
- cb5ffd04 2021-12-29 18:36:55 +0100 khanh.bui@elegosoft.com  (origin/feature_4100_blp1295_timeline-group-by-product-categories-or-partners-or-orders_v12) refactor timeline_renderer
- 48f493cb 2021-12-29 16:32:51 +0100 khanh.bui@elegosoft.com  refactor code 1
- e0851096 2021-12-29 14:39:45 +0100 khanh.bui@elegosoft.com  fix group by partner_id and order_name
- abf059d7 2021-12-28 18:57:57 +0100 khanh.bui@elegosoft.com  fix group by order_name
- a96d0ddd 2021-12-13 12:43:25 +0100 khanh.bui@elegosoft.com  (origin/wip_4100_product-groups-rental-timeline_v12) group by order_name
- dad8b1a7 2021-12-11 00:19:44 +0100 khanh.bui@elegosoft.com  grouping by partner_id
- aa6b2983 2021-12-08 11:07:23 +0100 khanh.bui@elegosoft.com  sorting product category in hierachy final
- 57ee12cb 2021-12-03 17:23:42 +0100 khanh.bui@elegosoft.com  fix collapse and expand parent groups
- 39c2ca9c 2021-11-30 15:19:23 +0100 khanh.bui@elegosoft.com  timeline by product_category_id
- 296b6193 2021-10-25 10:20:28 +0200 wagner@elegosoft.com  regenrate documentation (issue #4016)
- 43b06373 2021-10-10 18:18:11 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/feature_4447_blp1142_rental_product_variant_v12: addons-rental-vertical remotes/origin/feature_4447_blp1142_rental_product_variant_v12 - 35019a0969ffa6b2625ae89220590787266e85d7 [IMP] improve domain on smart buttons on Product.product form view, so inactivated product or related inactivated rental services also covered, (issue#4447)
- 35019a09 2021-09-29 09:47:59 +0200 cpatel@elegosoft.com  (origin/feature_4447_blp1142_rental_product_variant_v12) [IMP] improve domain on smart buttons on Product.product form view, so inactivated product or related inactivated rental services also covered, (issue#4447)
- 8b4d40c4 2021-09-23 09:19:24 +0200 wagner@elegosoft.com  regenerate doc (issue #4016)
- 5fddc156 2021-06-25 15:21:12 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/feature_4213_blp1110_timeline_filter_v12: addons-rental-vertical remotes/origin/feature_4213_blp1110_timeline_filter_v12 - cc3f88ac0f704ea56d61229ed238d9590b85f0db [IMP] add new field active for model product.timeline and implements the filter of it.
- cc3f88ac 2021-06-22 21:39:26 +0200 yweng@elegosoft.com  (origin/feature_4213_blp1110_timeline_filter_v12) [IMP] add new field active for model product.timeline and implements the filter of it.
- 6c3a7802 2021-06-22 20:38:48 +0200 yweng@elegosoft.com  [IMP] improves filter on field product_id for timeline (issue 4214)
- 91418bed 2021-06-22 12:23:09 +0200 yweng@elegosoft.com  [IMP] add filter for timeline (issue 4213)
- dd988a2f 2021-06-09 12:42:47 +0200 wagner@elegosoft.com  update documentation (issue #3613)
- 1abc79fe 2021-05-12 18:08:04 +0200 yweng@elegosoft.com  (origin/wip_4168_sale_rental_v12, wip_4168_sale_rental_v12) [IMP] adjust dependence of rental modules: replace rental_sale with sale_rental
- d9f3440e 2021-03-19 12:01:19 +0100 cpatel@elegosoft.com  (origin/feature_3954_blp1034_rental_timeline_v12) [IMP] update order name to timeline view, when order type is changed, (issue#3954)
- d4788ddb 2021-02-02 20:04:59 +0100 yweng@elegosoft.com  (origin/feature_3760_blp969_rental_timeline_v12) [IMP] black formatted (issue 3760)
- 4ff061a7 2021-02-02 20:00:30 +0100 yweng@elegosoft.com  [IMP] add trigger for updating of address fields of res.partner in product.timeline (issue 3760)
- b92f94f2 2021-02-02 17:36:38 +0100 yweng@elegosoft.com  [IMP] adjust trigger function to update infos in timeline (issue 3760)
- f82eb5d5 2021-02-01 17:07:51 +0100 yweng@elegosoft.com  [IMP] improves performance of timeline (issue 3760)
- bbd5cb25 2021-01-14 13:55:22 +0100 wagner@elegosoft.com  adapt gen-doc and update (issue #3613)
- a35a62d4 2020-12-22 22:59:30 +0100 kay.haeusler@elego.de  regenerate all de.po and \*.pot files; issue #4016
- 83ed8f72 2020-12-22 18:06:08 +0100 wagner@elegosoft.com  all Python code reformatted by black code formatter (issue #4016)
- 1bd390d6 2020-12-05 19:21:06 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/defect_3961_blp862_rental_timeline_v12: addons-rental-vertical remotes/origin/defect_3961_blp862_rental_timeline_v12 - 5b368fda8e6b6ecc26a6da20265e04fd3777f384 create timeline object if the option retal was set afterwards; issue #3961
- 5b368fda 2020-12-02 10:47:04 +0100 kay.haeusler@elego.de  (origin/defect_3961_blp862_rental_timeline_v12) create timeline object if the option retal was set afterwards; issue #3961
- 91434a65 2020-12-02 10:43:47 +0100 kay.haeusler@elego.de  fix a wrong compare (apples and oranges); issue #3961
- 28fa9958 2020-11-20 13:43:46 +0100 yweng@elegosoft.com  (origin/defect_3953_blp862_update_date_in_sale_order_line_v12) [FIX] fixs function _reset_timeline to update the date_start later.
- c7e3b592 2020-11-06 09:59:46 +0100 wagner@elegosoft.com  regenerate doc from manifests (issue #3613)
- 391ef2af 2020-10-28 20:59:58 +0100 wagner@elegosoft.com  add usage information for product sets and product packs; add configuration and usage information for rental_sale and extend gen-doc for configuration (issue #3613)
- d39f57e8 2020-10-28 20:18:47 +0100 wagner@elegosoft.com  add links to the index in README.md (issue #3613)
- b1039c8c 2020-10-28 17:39:27 +0100 wagner@elegosoft.com  add index generation and add index to README.md (issue #3613)
- 4610306e 2020-10-28 17:08:11 +0100 wagner@elegosoft.com  add usage information about the rental timeline view (issue #3613)
- 363cb502 2020-10-28 16:59:43 +0100 wagner@elegosoft.com  change quotes in manifests of rental_forward_shipment_plan and rental_routing and add some draft information about routing; regenerate (issue #3613)
- fb94de5c 2020-10-28 16:20:59 +0100 wagner@elegosoft.com  add descriptions to rental_timeline modules and regenerate (issue #3613)
- f1affe52 2020-10-28 12:45:28 +0100 wagner@elegosoft.com  regenerate doc (issue #3613)
- 5244748e 2020-10-27 14:52:26 +0100 wagner@elegosoft.com  regenerate documentation and add README.rst files (issue #3339)
- d02ea5d8 2020-10-27 14:41:06 +0100 wagner@elegosoft.com  (tag: bp_rental_v12_integration-cep-849) update doc generation script (issue #3339)
- adcc40f7 2020-10-07 10:19:08 +0200 maria.sparenberg@elegosoft.com  (origin/defect_3878_blp824_update_times_v12) issue #3878 fix arguments for update times because start date was also written as end date
- b7dad089 2020-10-06 13:48:11 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/fix_3884_blp819_fix_application_status_and_deps_v12: addons-rental-vertical remotes/origin/fix_3884_blp819_fix_application_status_and_deps_v12 - 7580ae8936652f96fb11ac212867967458a4e127 set application to false for all modules except rental_base (issue #3884, issue #3339)
- 7580ae89 2020-10-05 22:19:25 +0200 wagner@elegosoft.com  (origin/fix_3884_blp819_fix_application_status_and_deps_v12, fix_3884_blp819_fix_application_status_and_deps_v12) set application to false for all modules except rental_base (issue #3884, issue #3339)
- b4743f79 2020-10-05 16:13:02 +0200 maria.sparenberg@elegosoft.com  (origin/defect_3880_blp819_timeline_confirmed_so_v12) issue #3880 allow updating confirmed order lines and corresponding timeline entries and contract lines
- 79d9f43c 2020-10-02 14:02:24 +0200 maria.sparenberg@elegosoft.com  issue #3880 create timeline object for sale order lines in state 'sale'
- 1be4b54c 2020-09-15 12:08:18 +0200 yweng@elegosoft.com  (origin/feature_3866_blp804_rename_sale_rental_v12) [MIG] Rename Module sale_rental and rental_sale (update dependence and xml_id)
- 8cc4c7a8 2020-09-08 13:11:20 +0200 kay.haeusler@elego.de  (origin/defect_3863_blp776_recreating_timeline_items_v12) recreating the timeline items when the order is setting from cancel to draft; issue #3863
- a196d00c 2020-07-13 09:22:09 +0200 yweng@elegosoft.com  (origin/feature_3760_blp695_rental_menu_dashboard_v12) [IMP] add menu dashboard
- eee2472b 2020-06-26 19:24:51 +0200 wagner@elegosoft.com  (origin/fix_3339_blp669_extend_documentation_v12, origin/fix_3339_blp666_extend_documentation_v12, fix_3339_blp669_extend_documentation_v12, fix_3339_blp666_extend_documentation_v12) update documentation (issue #3339)
- e52be419 2020-06-24 12:33:36 +0200 yweng@elegosoft.com  (origin/defect_3729_blp662_sell_service_in_rental_order_v12) [IMP] adjust function _get_product_domain to sell normal service in rental order (issue 3729)
- 57b29fa1 2020-05-24 12:58:49 +0200 wagner@elegosoft.com  (origin/fix_3339_blp622_extend_documentation_v12, origin/fix_3339_bl616_extend_documentation_v12, fix_3339_blp622_extend_documentation_v12, fix_3339_bl616_extend_documentation_v12) update documentation for fix release (issue #3339)
- 94dc79ca 2020-05-16 18:10:44 +0200 wagner@elegosoft.com  (origin/fix_3339_blp559_extend_documentation_v12, fix_3339_blp559_extend_documentation_v12) update module documentation (issue #3339)
- 89adaaf3 2020-05-16 14:54:03 +0200 wagner@elegosoft.com  fixup categories and regenerate documentation (issue #3339)
- 5a1a6dc2 2020-05-06 09:52:48 +0200 maria.sparenberg@elegosoft.com  (origin/feature_3409_blp543_rental_timeline_colors_v12) issue #3409 change color in timeline view
- 134218b1 2020-05-03 18:34:51 +0200 wagner@elegosoft.com  (origin/feature_3339_blp541_update_doc_v12, feature_3339_blp541_update_doc_v12) unify license and author and regenerate documentation (issue #3613, issue #3339)
- 795b1b6a 2020-04-24 20:58:26 +0200 wagner@elegosoft.com  (tag: bp_rental_v12_integration-cep-521, tag: bp_rental_v12_integration-cep-520, tag: bp_rental_v12_integration-cep-519, tag: bp_rental_v12_integration-cep-518, tag: bp_rental_v12_integration-cep-517, tag: bp_rental_v12_integration-cep-516, tag: bp_rental_v12_integration-cep-514, tag: bp_rental_v12_integration-cep-513, tag: bp_rental_v12_integration-cep-512, tag: bp_rental_v12_integration-cep-511, tag: bp_rental_v12_integration-cep-510, tag: bp_rental_v12_integration-cep-509, tag: bp_rental_v12_integration-cep-508, tag: bp_rental_v12_integration-cep-507, tag: bp_rental_v12_integration-cep-506, tag: bp_rental_v12_integration-cep-505, tag: bp_humanilog_v12_integration-cep-322, tag: bp_humanilog_v12_integration-cep-321, tag: bp_humanilog_v12_integration-cep-320, tag: baseline_rental-vertical_v12_swrent_daily_build-503, origin/rental_v12_integration-cep-503, rental_v12_integration-cep-503) regenerate documentation (issue #3613)
- 7fac932a 2020-04-13 14:13:09 +0200 wagner@elegosoft.com  (origin/fix_3339_blp455_extend_documentation_v12, fix_3339_blp455_extend_documentation_v12) regenerate documentation (issue #3339)
- 2da340dc 2020-04-13 14:11:24 +0200 wagner@elegosoft.com  change license for rental-vertical to AGPL (issue #3339)
- 6d3410b3 2020-04-13 13:28:20 +0200 wagner@elegosoft.com  regenerate documentation (issue #3339)
- 0bab92d2 2020-04-09 12:41:12 +0200 wagner@elegosoft.com  (origin/fix_3339_blp355_extend_documentation_v12, fix_3339_blp355_extend_documentation_v12) update/regenerate addon documentation (issue #3339)
- b081ed15 2020-04-08 18:49:30 +0200 ycervantes@elegosoft.com  (origin/fix_3623_blp435_web_timeline_extend_v12) [ADD] custom view_type named rental_timeline
- 1430ab87 2020-04-07 12:14:14 +0200 ycervantes@elegosoft.com  [FIX] use extend instead of include in TimelineRenderer
- b0d605b6 2020-03-30 16:42:43 +0200 kay.haeusler@elego.de  (origin/feature_3409_blp420_rental_timeline_v12) remove the product_instance condition; issue #3409
- 3efeb14b 2020-03-24 17:40:06 +0100 kay.haeusler@elego.de  (origin/feature_3409_blp412_rental_timeline_v12) unlink also the entries in product.timeline if the main object is unlink; issue #3409
- 5533e368 2020-03-22 21:48:23 +0100 kay.haeusler@elego.de  (origin/feature_3409_blp400_rental_timeline_v12) open the dialogs in readonly mode; issue #3409
- db00762d 2020-03-20 22:42:06 +0100 kay.haeusler@elego.de  formated the fields date_start, date_end, type and product_instance_state; issue #3409
- 4c397d7e 2020-03-20 15:49:09 +0100 kay.haeusler@elego.de  fix the translations; issue #3409
- 036a10e3 2020-03-22 21:49:14 +0100 kay.haeusler@elego.de  remove unnecessary logger outputs; issue #3409
- c4ee80dd 2020-03-19 18:20:08 +0100 kay.haeusler@elego.de  workaround for removing the database ids in the mouse over in the timeline; issue #3591
- b49c01da 2020-03-15 10:12:53 +0100 wagner@elegosoft.com  (origin/fix_3339_blp384_extend_documentation_v12) regenerate doc (issue #3339)
- cea0e942 2020-03-13 20:38:19 +0100 wagner@elegosoft.com  update documentation to build 380 (issue #3339)
- 1d4b0b90 2020-03-11 21:29:48 +0100 kay.haeusler@elego.de  (origin/feature_3409_blp355_rental_timeline_v12) adjust the start point on clicking the scale buttons; issue #3409
- f3ea64ff 2020-03-11 21:28:40 +0100 kay.haeusler@elego.de  fix the order_name; issue #3409
- e371276d 2020-03-10 18:14:07 +0000 jenkins-ci@elegosoft.com  [MERGE] remotes/origin/fix_3339_blp343_extend_documentation_v12: addons-rental-vertical remotes/origin/fix_3339_blp343_extend_documentation_v12 - 9576b54fbb0cbcbffb804587fd722df8a4057da0 allow cli overwrite of module arguments; regenerate doc for rental_product_instance_appointment rental_product_variant rental_offday rental_invoice rental_contract_month rental_contract (issue #3339)
- 5fc8c62f 2020-03-08 18:26:39 +0100 kay.haeusler@elego.de  outsource the displaying of the icons to two separate modules; issue #3409
- 804dc443 2020-03-07 21:06:12 +0100 wagner@elegosoft.com  regenerate module documentation (issue #3339)
- 6fd1771a 2020-03-06 20:32:25 +0100 kay.haeusler@elego.de  (origin/feature_3462_blp333_renaming_addons_v12) rename and split some addons; issue #3462

