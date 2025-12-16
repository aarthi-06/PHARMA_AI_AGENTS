def parse_clinical_trials(raw_data: dict) -> dict:
    studies = raw_data.get("studies", [])

    summary = {
        "active": 0,
        "completed": 0,
        "phase_distribution": {
            "Observational": 0,
            "Phase 1": 0,
            "Phase 2": 0,
            "Phase 3": 0,
            "Phase 4": 0
        }
    }

    details = []

    for study in studies:
        ps = study.get("protocolSection", {})

        ident = ps.get("identificationModule", {})
        status_mod = ps.get("statusModule", {})
        design = ps.get("designModule", {})
        sponsor_mod = ps.get("sponsorCollaboratorsModule", {})
        contacts_mod = ps.get("contactsLocationsModule", {})

        # Basic info
        trial_id = ident.get("nctId")
        title = ident.get("officialTitle") or ident.get("briefTitle") or "Not available"

        # Status
        status_raw = status_mod.get("overallStatus")
        status = "Completed" if status_raw == "COMPLETED" else "Active"

        # Dates
        start_date = status_mod.get("startDateStruct", {}).get("date")
        end_date = (
            status_mod.get("completionDateStruct", {}).get("date")
            or status_mod.get("primaryCompletionDateStruct", {}).get("date")
        )

        # Study type & Phase
        study_type = design.get("studyType")
        if study_type == "OBSERVATIONAL":
            phase = "Observational"
            summary["phase_distribution"]["Observational"] += 1
        else:
            # Interventional study with phases
            phases = design.get("phases", [])
            phase = phases[0].replace("PHASE", "Phase ") if phases else "Unknown"
            if phase in summary["phase_distribution"]:
                summary["phase_distribution"][phase] += 1

        # Status summary count
        if status == "Completed":
            summary["completed"] += 1
        else:
            summary["active"] += 1

        # Sponsor
        sponsor = sponsor_mod.get("leadSponsor", {}).get("name") or "Not available"

        # Locations
        locations = []
        loc_list = contacts_mod.get("locations", [])
        for loc in loc_list:
            country = loc.get("country")
            if country:
                locations.append(country)
        if not locations:
            locations = ["Not available"]

        
        loc = list(set(locations))

        # Append to details
        details.append({
            "trial_id": trial_id or "Not available",
            "title": title,
            "status": status,
            "phase": phase,
            "sponsor": sponsor,
            "locations": loc,
            "start_date": start_date or "Not available",
            "end_date": end_date or "Not available"
        })

    return {
        "trials": {
            "summary": summary,
            "details": details,
            "notes": "Parsed deterministically from ClinicalTrials.gov"
        }
    }
