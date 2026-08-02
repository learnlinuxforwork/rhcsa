<div align="center">

<img src="https://free.learnlinuxforwork.com/assets/img/ST-Brain-Logo.png" alt="Shea's Tech" width="120">

# Free RHCSA Course

### Zero to Red Hat Certified System Administrator

**Twelve weeks. Twelve hands-on lab guides. Every exam objective.**
Built for people who can't drop $3,000 on a training course.

[**rhcsa.learnlinuxforwork.com**](https://rhcsa.learnlinuxforwork.com) · [Download the eBook](Free_RHCSA_Course_eBook.pdf) · [Why I built this](https://rhcsa.learnlinuxforwork.com/#story)

[![Exam](https://img.shields.io/badge/exam-EX200-cc0000?style=flat-square)](https://www.redhat.com/en/services/training/ex200-red-hat-certified-system-administrator-rhcsa-exam)
[![Platform](https://img.shields.io/badge/platform-RHEL%2010-cc0000?style=flat-square)](https://developers.redhat.com/products/rhel/download)
[![License](https://img.shields.io/badge/license-AGPL--3.0--or--later-cc0000?style=flat-square)](LICENSE)
[![Cost](https://img.shields.io/badge/cost-%240-cc0000?style=flat-square)](#what-it-costs)
[![Tracking](https://img.shields.io/badge/tracking-none-cc0000?style=flat-square)](#features)
[![PRs](https://img.shields.io/badge/PRs-welcome-cc0000?style=flat-square)](#contributing)

<br>

| 12 | 12 | 10 | $0 |
|:--:|:--:|:--:|:--:|
| **weeks** | **lab guides** | **exam domains** | **to start** |

</div>

---

## Quick start

```bash
git clone https://github.com/learnlinuxforwork/rhcsa.git && cd rhcsa
./scripts/build-local-lab.sh      # builds both lab VMs in VirtualBox
python3 -m http.server 8000       # read the course at localhost:8000
```

Then open [Lab Guide 1](lab/week-01.html) and start typing. Prefer paper or offline?
[Download the eBook](Free_RHCSA_Course_eBook.pdf) — 34 pages, every link clickable.

---

## The one thing that matters

> **Configurations must persist after reboot without intervention.**

That sentence is in Red Hat's own objectives, and it fails more candidates than any
technical topic. A mount that works until you reboot scores zero. A service that runs
but isn't enabled scores zero. Every lab in this course ends with a reboot check, because
the exam grades the *state of the machine*, not the commands you typed.

---

## What's inside

**Thirteen sections**, built to the same shape as the [Free DevOps Roadmap](https://free.learnlinuxforwork.com):

| # | Section | What it gives you |
|:--|:--|:--|
| 01 | How This Course Works | Pacing options from 6 to 18 weeks, and where the hours actually go |
| 02 | What the RHCSA Actually Is | Format, conditions, and what the graders care about |
| 03 | Build Your Home Lab | Hypervisors, VM sizing, the two-machine topology, hardware if you need it |
| 04 | Self-Managed Cloud Hosted Labs | The same lab on GCP, DigitalOcean, AWS, or Vultr |
| 05 | The Certification Ladder | Linux Essentials, Linux+, LFCS — plus **DoD 8140** for government contractors |
| 06 | Exam Objective Coverage Map | All ten Red Hat domains mapped to the week that covers them |
| 07 | The 12-Week Plan | 99 checkable tasks, progress saved in your browser |
| 08 | Lab Guides | Twelve standalone guides — commands, verification, break/fix |
| 09 | Core Resource List | 58 linked resources, free and low-cost |
| 10 | Estimated Costs | Honest numbers, optional items marked |
| 11 | Exam Day | Habits that get you there, plus the morning-of checklist |
| 12 | Why I Built This Guide | The reason this is free |
| 13 | Credits and Trademarks | Everyone whose work this stands on |

---

## The twelve weeks

| Week | Focus | Red Hat domain |
|:--:|:--|:--|
| 1 | Essential Tools and the Shell | Understand and use essential tools |
| 2 | Users, Groups, and Privileged Access | Manage users and groups |
| 3 | Software: RPM, Repositories, and Flatpak | Manage software |
| 4 | Processes, Tuning, and Scheduled Tasks | Operate running systems |
| 5 | Boot, Targets, Services, and Recovery | Operate running systems |
| 6 | Logs, Journals, and Time | Operate running systems |
| 7 | Networking and firewalld | Manage basic networking |
| 8 | Partitions, Filesystems, and Swap | Configure local storage |
| 9 | LVM, NFS, and autofs | Create and configure file systems |
| 10 | SELinux, SSH Keys, and Default Permissions | Manage security |
| 11 | Shell Scripting | Create simple shell scripts |
| 12 | Mock Exam, Remediation, and Exam Day | All of it, under exam conditions |

> **Flatpak is on the RHEL 10 exam.** Most study material predates that. Week 3 covers it.

---

## The twelve lab guides

Every week has a standalone guide. Same shape each time: what you're building, the real
commands, how to verify it, a **break/fix drill** where you sabotage the system on purpose
and repair it, then a reboot check.

| | Guide | Time | You'll break and fix |
|:--:|:--|:--|:--|
| 1 | [Essential Tools and the Shell](lab/week-01.html) | 2–3 h | A directory you `chmod 000`'d and locked yourself out of |
| 2 | [Users, Groups, and Privileged Access](lab/week-02.html) | 2–3 h | A malformed `sudoers.d` file that kills privilege escalation |
| 3 | [Software: RPM, Repos, and Flatpak](lab/week-03.html) | 2–3 h | A repo pointing at a path that doesn't exist |
| 4 | [Processes, Tuning, and Scheduled Tasks](lab/week-04.html) | 2–3 h | A systemd timer with a bad directive |
| 5 | [Boot, Targets, Services, and Recovery](lab/week-05.html) | 3–4 h | A disabled service that never comes back after reboot |
| 6 | [Logs, Journals, and Time](lab/week-06.html) | 2–3 h | A volatile journal that discards yesterday's evidence |
| 7 | [Networking and firewalld](lab/week-07.html) | 3–4 h | A firewall rule added without `--permanent` |
| 8 | [Partitions, Filesystems, and Swap](lab/week-08.html) | 3–4 h | An `fstab` entry that would strand the machine at boot |
| 9 | [LVM, NFS, and autofs](lab/week-09.html) | 4–5 h | An `lvextend` that fails because the VG has no room |
| 10 | [SELinux, SSH Keys, and Permissions](lab/week-10.html) | 4–5 h | A `chcon` fix that `restorecon` silently undoes |
| 11 | [Shell Scripting](lab/week-11.html) | 3–4 h | A missing semicolon before `then` |
| 12 | [Mock Exam and Exam Day](lab/week-12.html) | 6–8 h | Skipping the reboot — and scoring yourself wrong |

---

## Working for a U.S. government contractor?

**DoD 8140** (which replaced DoD 8570.01-M) decides whether you can hold a privileged
account on DoD systems. For a Linux administrator, **privileged user access (PUA)**
generally needs two certifications, not one:

| | Requirement | Typical certification |
|:--|:--|:--|
| 1 | Baseline security certification for the work role | [CompTIA Security+](https://www.comptia.org/en-us/certifications/security/), then [CySA+](https://www.comptia.org/en-us/certifications/cybersecurity-analyst/) for higher tiers |
| 2 | Computing environment (CE) certification for the platform | **RHCSA** — the standard for Red Hat estates |

**RHCSA + Security+** is the pairing on most federal Linux sysadmin postings. Many
contractors won't onboard you to a privileged role until you hold both — and quite a few
will pay for the second once you have the first.

> ⚠️ **Verify before you spend.** 8140 moved to a work-role-based framework and the
> approved lists change. Check the [DoD Cyber Exchange](https://public.cyber.mil/wid/dod8140/)
> and confirm with your FSO or contract lead before booking an exam on this basis.

---

## Build the lab in one command

Three scripts in [`scripts/`](scripts/). All of them create the same two machines —
`servera` and `serverb` — with the spare 10 GB disk that Weeks 8 and 9 need.

```bash
./scripts/build-local-lab.sh                    # VirtualBox, ISO from /rhcsa-labs
./scripts/build-local-lab.sh --provider vmware  # VMware Workstation Pro
./scripts/build-cloud-lab.sh gcp                # or: do | aws | vultr
./scripts/build-podman-lab.sh                   # containers, for low-RAM machines
```

Every script takes `--destroy` to tear it all down and start clean.

| Script | Builds | Good for |
|:--|:--|:--|
| `build-local-lab.sh` | Two VMs in **VirtualBox** or **VMware Workstation Pro**, ISOs read from `/rhcsa-labs` | All 12 weeks |
| `build-cloud-lab.sh` | The same pair on **Google Cloud**, **DigitalOcean**, **AWS**, or **Vultr** | Weeks 1–4, 6–12 |
| `build-podman-lab.sh` | Two **Rocky Linux 10 Podman containers** with systemd | Weeks 1–4, 10, 11 |

> **The container lab is honest about its limits.** Containers share the host kernel, so
> partitioning, LVM, filesystems, the bootloader, boot targets, and firewalld genuinely
> do not work there. Weeks 5–9 need real VMs. The script says so rather than pretending.

### Self-managed cloud hosted labs

If the laptop can't spare the RAM, rent the lab instead. Same two machines, same spare
disk, firewall rules that let them talk and SSH locked to your address.

| Provider | Why | Command |
|:--|:--|:--|
| [Google Cloud](https://console.cloud.google.com/) | Rocky 10 images in `rocky-linux-cloud`, no marketplace hunting. New accounts get credit. | `./build-cloud-lab.sh gcp` |
| [DigitalOcean](https://cloud.digitalocean.com/) | Simplest pricing, Rocky 10 in the catalogue, clean block volumes for LVM week | `./build-cloud-lab.sh do` |
| [AWS](https://console.aws.amazon.com/) | Rocky 10 AMIs, script finds the newest for your region. Free tier won't cover `t3.medium`. | `./build-cloud-lab.sh aws` |
| [Vultr](https://my.vultr.com/) | Cheapest hourly if you're disciplined about destroying it | `./build-cloud-lab.sh vultr` |

> 💸 **Set a billing alert on day one.** Every provider offers one free, and every provider
> will happily bill you for an instance you forgot about. `--destroy` between study sessions.
>
> **Do Week 5 locally regardless.** Console work — `rd.break`, root password recovery,
> editing the bootloader — needs a hypervisor where you control the virtual console.

### Which operating system

| | Role | Why |
|:--|:--|:--|
| **RHEL 10** | Guest — practise on this | The actual exam platform. The [Developer Subscription](https://developers.redhat.com/products/rhel/download) is free for **16 systems**. |
| **Rocky Linux 10** | Guest — free alternative | Community RHEL rebuild. Same commands, no account needed. |
| **Ubuntu** | **Host** — runs the VMs | Easiest Linux to put on the laptop or server that hosts your lab. Not for exam practice — different package manager and defaults. |

---

## Run it locally

No build step, no dependencies, no framework.

```bash
git clone https://github.com/learnlinuxforwork/rhcsa.git
cd rhcsa
python3 -m http.server 8000
```

Open <http://localhost:8000>. Opening `index.html` over `file://` won't work — the page
fetches `data/rhcsa.json` and browsers block that over the file protocol.

---

## Features

- **Dark and light mode** — follows your system, toggle overrides it, choice persists
- **Progress tracking** — 99 checkboxes, per-week rings, overall bar. Stored in `localStorage`
- **No tracking, no cookies, no analytics, no third-party scripts.** Zero JS dependencies
- **Keyboard and screen-reader friendly** — skip link, focus rings, `aria-expanded` accordions
- **Prints cleanly** — every lab guide is print-ready if you'd rather work from paper

---

## What it costs

| Item | Estimate |
|:--|:--|
| This course, all 12 lab guides, and the eBook | **$0** |
| RHEL 10 Developer Edition (16 systems) or Rocky Linux 10 | **$0** |
| Lab VMs on hardware you already own | **$0** |
| [RHCSA exam (EX200)](https://www.redhat.com/en/services/training/ex200-red-hat-certified-system-administrator-rhcsa-exam) | ~$500 |
| Cloud lab, if your laptop can't host VMs | ~$10–25/month, less if you destroy it between sessions |
| Linux Essentials / Linux+ / LFCS confidence builders | Optional — the last two together cost more than the RHCSA itself |
| [CompTIA Security+](https://www.comptia.org/en-us/certifications/security/) — if you need DoD 8140 privileged access | ~$404 · often employer-funded |
| [CompTIA CySA+](https://www.comptia.org/en-us/certifications/cybersecurity-analyst/) — higher-tier work roles | ~$425 · optional, usually employer-funded |

---

## What's in the resource list

58 links across ten categories, all free or genuinely low-cost:

| Category | Includes |
|:--|:--|
| The authoritative source | EX200 objectives, Red Hat docs, Red Hat Interactive Labs |
| Getting the operating system | RHEL 10 Developer Edition, Rocky Linux, Ubuntu |
| Hypervisors and home lab | VirtualBox, VMware Workstation, KVM, UTM, Proxmox, OpenNebula |
| Hardware — used and new | Back Market, Renew4me, NurTech, Refurb.me, Mac of All Trades, System76, Framework, ThinkPad |
| Practice under pressure | LinuxCert Guru, LabEx, KodeKloud, Learn Linux For Work labs |
| Training and community | Learn Linux For Work, Doc Linux, Kubecraft Linux, The Hood, r/linuxadmin |
| The confidence-builder exams | LPI Linux Essentials, CompTIA Linux+, LFCS, killer.sh |
| Scripting and fundamentals | Automate the Boring Stuff, Pro Git, OverTheWire Bandit, Google SRE Book |
| Cloud providers | GCP, DigitalOcean, AWS, Vultr, and each CLI |
| U.S. government contracting | DoD Cyber Exchange, Security+, CySA+, Red Hat cert verification |

---

## Why this exists

> This was built for that fundi in Kenya, that hustler in Nigeria, the determined in
> Rwanda or Ethiopia. The hungry surviving in the UAE. The Indonesian or Filipino brother
> or sister — determined, but never given a chance or guidance.
>
> It could be that street vendor in East London, West or North Philadelphia, the hoods of
> NJ, or in New York City. Or that front-desk hotel worker dreaming of changing their life.

Shea is 100% self-taught. He left the U.S. Navy — where he served as a Hospital Corpsman
and Fleet Marine Force combat medic — with no IT experience and no money for bootcamps.
Video training was what finally worked. This course is the thing he wishes had existed.

[Read the whole story →](https://rhcsa.learnlinuxforwork.com/#story)

---

## Deployment

Push to `main` → [`.github/workflows/pages.yml`](.github/workflows/pages.yml) validates
`data/rhcsa.json`, confirms all twelve lab guides exist, runs the scope check, and deploys
to GitHub Pages at [rhcsa.learnlinuxforwork.com](https://rhcsa.learnlinuxforwork.com).

First-time setup:

1. **Settings → Pages → Source:** GitHub Actions
2. **Settings → Pages → Custom domain:** `rhcsa.learnlinuxforwork.com`, then tick *Enforce HTTPS*
3. DNS: `CNAME` record `rhcsa` → `learnlinuxforwork.github.io`

The [`CNAME`](CNAME) file keeps the domain set across deploys — don't delete it.

---

## Project structure

```
.
├── index.html                    the UI shell
├── assets/
│   ├── css/style.css             design tokens + dark/light themes
│   └── js/{app,lab}.js           renderer, progress tracking, theme toggle
├── data/rhcsa.json               ← all course content lives here
├── lab/week-01..12.html          generated lab guides (committed)
├── scripts/                      local, cloud, and container lab builders
├── tools/build_labs.py           regenerates lab/ from its LABS list
└── .github/workflows/pages.yml   validate → check labs → deploy
```

**To change course content, edit [`data/rhcsa.json`](data/rhcsa.json).** To change a lab
guide, edit the `LABS` list in [`tools/build_labs.py`](tools/build_labs.py) and re-run it.

---

## Contributing

Corrections, dead-link fixes, and clearer task wording are all welcome.

1. Fork and branch
2. Edit `data/rhcsa.json` (or the CSS/JS for interface changes)
3. Validate: `python3 -c "import json;json.load(open('data/rhcsa.json'))"`
4. Open a PR describing what changed and why

Keep the tone plain and practical. Keep resources free or genuinely low-cost, and
disclose affiliate relationships in the PR description — some links here are affiliate
links, they cost you nothing extra, and they keep this free.

---

## Content and licensing

All course text, lab guides, and scripts are **original work**, written for this
repository. They are built from
[Red Hat's published EX200 objectives](https://www.redhat.com/en/services/training/ex200-red-hat-certified-system-administrator-rhcsa-exam)
— the authoritative statement of what the exam covers — and from hands-on practice.
**No third-party book, course, or training material is reproduced here.**

Licensed under the **GNU AGPL v3.0 or later**. See [LICENSE](LICENSE). Free forever.

---

## Credits and trademarks

This is an independent, community-written study guide. It is **not affiliated with,
sponsored by, endorsed by, or certified by** Red Hat, Inc. or any other organisation
named here.

| Mark | Belongs to |
|:--|:--|
| Red Hat, RHEL, RHCSA, RHCE, EX200 | [Red Hat, Inc.](https://www.redhat.com/) |
| Rocky Linux | [Rocky Enterprise Software Foundation](https://rockylinux.org/) |
| Ubuntu | [Canonical Ltd.](https://ubuntu.com/) |
| VirtualBox | [Oracle Corporation](https://www.virtualbox.org/) |
| VMware Workstation Pro, Fusion | [Broadcom Inc.](https://www.vmware.com/) |
| Proxmox VE | Proxmox Server Solutions GmbH |
| Podman | [Red Hat, Inc.](https://podman.io/) and the Podman community |
| CompTIA, Security+, CySA+, Linux+ | [CompTIA, Inc.](https://www.comptia.org/) |
| DoD 8140, DoD 8570.01-M | [U.S. Department of Defense](https://public.cyber.mil/wid/dod8140/) |
| Linux Foundation, LFCS | [The Linux Foundation](https://www.linuxfoundation.org/) |
| LPI, Linux Essentials | [Linux Professional Institute](https://www.lpi.org/) |
| killer.sh | [killer.sh](https://killer.sh/) |
| Linux | Linus Torvalds |

All marks are the property of their respective owners. Their use here is nominative — to
identify the products this course teaches you to use — and implies no affiliation or
endorsement. Full credit table in [section 13](https://rhcsa.learnlinuxforwork.com/#credits).
If you own one of these marks and want the wording changed,
[open an issue](https://github.com/learnlinuxforwork/rhcsa/issues) and it will be fixed.

---

<div align="center">

### Related

[**Free DevOps Roadmap**](https://free.learnlinuxforwork.com) · 54 weeks, Linux to AWS DevOps — RHCSA is its Phase 0<br>
[**Learn Linux For Work**](https://www.learnlinuxforwork.com) · structured, work-focused Linux training<br>
[**Doc Linux**](https://learnlinuxforwork.com/doc-linux) · command reference and syntax lookups<br>
[**LinuxCert Guru**](https://linuxcert.guru/) · hands-on RHCSA mock exams<br>
[**Kubecraft Linux**](https://www.skool.com/linux/classroom) · Linux and Kubernetes community classroom

<br>

Built by **Shea** · [Shea's Tech](https://www.sheastech.io) · [LinkedIn](https://www.linkedin.com/in/sheastech/) · [YouTube](https://www.youtube.com/@sheastech?sub_confirmation=1)

*If anything here is wrong, report it and we'll fix it.*

</div>
