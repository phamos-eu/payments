frappe.listview_settings["Kefiya Bank Statement Import"] = {
    get_indicator: function(doc) {
        if (doc.status === "Not Started") {
            return [__("Not Started"), "grey", "status,=,Not Started"];
        } else if (doc.status === "Success") {
            return [__("Success"), "green", "docstatus,=,Success"];
        } else if (doc.status === "Partial Success") {
            return [__("Partial Success"), "orange", "status,=,Partial Success"];
        } else if (doc.status === "Error") {
            return [__("Error"), "red", "status,=,Error"];
        } 
    }
};
