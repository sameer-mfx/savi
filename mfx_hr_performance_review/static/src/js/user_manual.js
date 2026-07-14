/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

class HrPerformanceUserManual extends Component {
    setup() {
        this.state = useState({
            currentSection: 'overview',
        });
    }

    scrollToSection(ev) {
        const sectionId = ev.currentTarget.dataset.section;
        if (sectionId) {
            this.state.currentSection = sectionId;
            const el = document.getElementById(sectionId);
            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    }

    printManual() {
        window.print();
    }
}

HrPerformanceUserManual.template = "mfx_hr_performance_review.UserManualTemplate";

registry.category("actions").add("hr_performance_user_manual", HrPerformanceUserManual);
