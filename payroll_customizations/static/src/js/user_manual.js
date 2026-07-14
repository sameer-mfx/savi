/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class HrPayrollUserManual extends Component {
    setup() {
        this.currentSection = null;
    }

    scrollToSection(ev) {
        const sectionId = ev.currentTarget.dataset.section;
        const el = document.getElementById(sectionId);
        if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }

    printManual() {
        window.print();
    }
}

HrPayrollUserManual.template = "payroll_customizations.UserManualPage";
registry.category("actions").add("hr_payroll_user_manual", HrPayrollUserManual);
