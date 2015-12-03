from django.apps import AppConfig

from permissions.roles import register_role


charge_owner_actions = [
    'charge.read',
    'job.cancel',
    'job.comment',
    'job.delete',
    'job.detail',
    'job.list',
    'job.ownerapprove',
    'job.price',
    'job.read',
    'job.update',
    'line_item.read',
    'quote.delete',
    'quote.read',
    'user.read',
]

plan_user_actions = [
    'forge.read',
    'forge_profile.read',
    'location.read',
    'material_profile.read',
    'fdm_tool.read',
    'plan.read',
    'print_choice.read',
    'print_option.read',
    'tech_profile.read',
]

plan_privileged_actions = plan_user_actions + [
    'job.free_order'
]

plan_manage_actions = plan_user_actions + [
    'plan.manage',
]

plan_workflow_actions = plan_manage_actions + [
    'design.read',
    'design_spec.create',
    'design_spec.read',
    'job.cancel',
    'job.comment',
    'job.complete',
    'job.deny',
    'job.fail',
    'job.markpaid',
    'job.notify',
    'job.prioritize',
    'job.quote',
    'job.read',
    'job.refund',
    'job.reusecharge',
    'job.start',
    'job.systemapprove',
    'job.uncomment',
    'job.update',
    'line_item.create',
    'line_item.read',
    'mfg_profile.create',
    'mfg_profile.process',
    'mfg_profile.read',
    'quote.read',
    'tech_spec.read',
    'plan.workflow'
]

plan_settings_actions = plan_manage_actions + [
    'forge.unregister',
    'forge.create',
    'forge.update',
    'forge_profile.create',
    'forge_profile.update',
    'forge_profile.delete',
    'group.read',
    'group.update',
    'group.invite',
    'group.uninvite',
    'group.create',
    'group.delete',
    'location.create',
    'location.delete',
    'location.update',
    'material_profile.create',
    'material_profile.update',
    'material_profile.delete',
    'plan.update',
    'print_choice.create',
    'print_choice.update',
    'print_choice.delete',
    'print_option.create',
    'print_option.update',
    'print_option.delete',
    'tech_profile.create',
    'tech_profile.delete',
    'tech_profile.update',
    'user.credit',
    'user.read',
    'user.invite',
]

design_user_actions = [
    'design.create',
    'design.read',
    'design_spec.create',
    'design_spec.read',
    'job.create',
    'mfg_profile.create',
    'mfg_profile.process',
    'mfg_profile.read',
    'quote.create',
    'tech_spec.create',
    'tech_spec.read',
]

design_owner_actions = design_user_actions + [
    'design.delete',
    'design.forget',
    'design.update',
    'design.share',
]


class PermissionsConfig(AppConfig):
    name = 'permissions'
    verbose_name = "Permissions"

    def ready(self):
        # Charge based
        register_role('charge.owner', charge_owner_actions)

        # Design based
        register_role('design.public', design_user_actions)
        register_role('design.owner', design_owner_actions)

        # Plan based
        register_role('plan.owner', list(set(
            plan_workflow_actions + plan_settings_actions
        )))
        register_role('plan.settings_manager', plan_settings_actions)
        register_role('plan.workflow_manager', plan_workflow_actions)
        register_role('plan.privileged_user', plan_privileged_actions)
        register_role('plan.user', plan_user_actions)
