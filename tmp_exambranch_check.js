
    (function () {
        const lessonStorageKey = 'examBranchTeachingPlan';
        const evaluationStorageKeys = {
            '1': 'examBranchEvaluationData',
            '2': 'examBranchEvaluationDataSecond',
            '3': 'examBranchEvaluationDataThird',
            '4': 'examBranchEvaluationDataFourth'
        };
        let activeEvaluationSheet = '1';
        const legacyTimeTableStorageKeys = ['examBranchTimeTableData', 'examBranchTimeTableDataNoSameHourRepeatsV2', 'examBranchTimeTableDataCompleteR22ThreeOneITV3', 'examBranchTimeTableDataCompleteR22ThreeOneITV4', 'examBranchTimeTableDataMainIndividualMatchV5', 'examBranchTimeTableDataR25FullLoadV6', 'examBranchTimeTableDataR25PowerBILoadV7', 'examBranchTimeTableDataAIMLOSLibraryV8', 'examBranchTimeTableDataActivitiesLastHourV9', 'examBranchTimeTableDataActivitiesLastHourV10', 'examBranchTimeTableDataSectionsProjectV11', 'examBranchTimeTableDataNoFourthYearProjectsV12', 'examBranchTimeTableDataAllowedContextsV13', 'examBranchTimeTableDataActivityPlacementV14', 'examBranchTimeTableDataNoLabClashesV15', 'examBranchTimeTableDataRequirementRepairV16', 'examBranchTimeTableDataRequiredLabsV17', 'examBranchTimeTableDataFixedLayoutsV18', 'examBranchTimeTableDataLoadSummaryV19', 'examBranchTimeTableDataPinnedFixedLayoutsV20', 'examBranchTimeTableDataR22DataMiningLabV22'];
        const timeTableStorageKey = 'examBranchTimeTableDataR22DataMiningLabV23';
        const subjectSelectionStorageKey = 'examBranchFacultySubjectSelection';
        const labTimeTablePurgeFlag = 'examBranchLabTimeTablePurgeV1';

        // Keep the one-time initial cleanup limited to legacy keys. Current saved
        // timetables are migrated and repaired below instead of discarded.
        if (!localStorage.getItem(labTimeTablePurgeFlag)) {
            legacyTimeTableStorageKeys.forEach(function (key) {
                localStorage.removeItem(key);
            });
            localStorage.setItem(labTimeTablePurgeFlag, '1');
        }
        const lessonPlanDownloadUrl = "{% url 'dashboard:exam_branch_download_lesson_plan' %}";
        const evaluationWorkbookDownloadUrl = "{% url 'dashboard:exam_branch_download_evaluation' %}";
        const syllabusSubjectsUrl = "{{ syllabus_subjects_url }}";
        const csrfTokenValue = '{{ csrf_token }}';

        const lessonHeaderFields = {
            branch: document.getElementById('lessonBranch'),
            year: document.getElementById('lessonYear'),
            semester: document.getElementById('lessonSemester'),
            faculty: document.getElementById('lessonFaculty'),
            employeeCode: document.getElementById('lessonEmployeeCode'),
            subject: document.getElementById('lessonSubject'),
            className: document.getElementById('lessonClassName'),
            subjectCode: document.getElementById('lessonSubjectCode')
        };

        const lessonPlanBody = document.getElementById('teachingPlanBody');
        const lessonPlanStatus = document.getElementById('lessonPlanStatus');
        const labTimeTableStatus = document.getElementById('labTimeTableStatus');
        const evaluationSaveStatus = document.getElementById('evaluationSaveStatus');
        const evaluationSheetSelect = document.getElementById('evaluationSheetSelect');
        const timeTableStatus = document.getElementById('timeTableStatus');

        // Keep the Evaluation pane independent from Lesson Plan even if a browser
        // repairs legacy malformed markup differently. Moving the pane also moves
        // Internal Evaluations 1-4 as one unit under the Evaluation tab.
        const examBranchTabsContent = document.getElementById('examBranchTabsContent');
        const evaluationPane = document.getElementById('evaluation');
        const subjectSelectionPane = document.getElementById('subject-selection');
        if (examBranchTabsContent && evaluationPane && evaluationPane.parentElement !== examBranchTabsContent) {
            examBranchTabsContent.insertBefore(evaluationPane, subjectSelectionPane || null);
        }
        
        // Get all three marks body elements
        const marksBodyMap = {
            '1': document.getElementById('marksBody1'),
            '2': document.getElementById('marksBody2'),
            '3': document.getElementById('marksBody3'),
            '4': document.getElementById('marksBody4')
        };
        const marksBody = marksBodyMap['1']; // Default for backward compatibility
        
        // Get all evaluation sections
        const evaluationSectionsMap = {
            '1': document.querySelector('[data-sheet="1"]'),
            '2': document.querySelector('[data-sheet="2"]'),
            '3': document.querySelector('[data-sheet="3"]'),
            '4': document.querySelector('[data-sheet="4"]')
        };

        const evaluationSubjectNameMap = {
            '1': document.getElementById('evaluationSubjectName1'),
            '2': document.getElementById('evaluationSubjectName2'),
            '3': document.getElementById('evaluationSubjectName3'),
            '4': document.getElementById('evaluationSubjectName4')
        };
        
        // Get all grade summary tables
        const gradeSummaryTableMap = {
            '1': document.getElementById('gradeSummaryTable1'),
            '2': document.getElementById('gradeSummaryTable2'),
            '3': document.getElementById('gradeSummaryTable3'),
            '4': document.getElementById('gradeSummaryTable4')
        };
        const gradeSummaryTable = gradeSummaryTableMap['1']; // Default for backward compatibility
        const timeTableSlots = Array.from(document.querySelectorAll('.timetable-slot'));
        const emptyTimeTableCards = Array.from(document.querySelectorAll('[data-empty-timetable-card]'));
        const timeTableMetaFields = Array.from(document.querySelectorAll('.timetable-meta-input'));
        const primaryFixedTimeTableSpec = {
            regulation: 'R22',
            year: '3',
            semester: '2',
            branch: 'IT',
            section: ''
        };
        const individualTimeTableContainer = document.getElementById('individualTimeTableContainer');
        const individualTimeTableTemplate = individualTimeTableContainer
            ? individualTimeTableContainer.querySelector('[data-individual-timetable-card]').cloneNode(true)
            : null;
        const syllabusSubjectCount = document.getElementById('syllabusSubjectCount');
        const syllabusSubjectSelect = document.getElementById('syllabusSubjectSelect');
        const courseReferenceBody = document.getElementById('courseReferenceBody');
        const timeTableYearField = document.getElementById('timeTableYear');
        const timeTableSemesterField = document.getElementById('timeTableSemester');
        const timeTableBranchField = document.getElementById('timeTableBranch');
        const mainTimeTableDownloadButtons = Array.from(document.querySelectorAll('[data-download-main-timetable]'));
        const subjectSelectionForm = document.getElementById('facultySubjectSelectionForm');
        const subjectSelectionStatus = document.getElementById('subjectSelectionStatus');
        const subjectSelectionPreviewBody = document.getElementById('subjectSelectionPreviewBody');
        const subjectSelectionCount = document.getElementById('subjectSelectionCount');
        const subjectSelectionFields = {
            facultyName: document.getElementById('subjectFacultyName'),
            employeeCode: document.getElementById('subjectEmployeeCode'),
            branch: document.getElementById('subjectSelectionBranch'),
            section: document.getElementById('subjectSelectionSection'),
            regulation: document.getElementById('subjectSelectionRegulation'),
            year: document.getElementById('subjectSelectionYear'),
            semester: document.getElementById('subjectSelectionSemester'),
            subjectName: document.getElementById('subjectSelectionName'),
            labRoomNumber: document.getElementById('subjectLabRoomNumber'),
            timesTaught: document.getElementById('subjectTimesTaught'),
            previousResult: document.getElementById('subjectPreviousResult')
        };
        const periodOrder = ['9:30-10:30', '10:30-11:30', '11:40-12:40', '1:20-2:15', '2:15-3:10', '3:15-4:10'];
        const departmentBranches = ['CSE', 'AIML', 'IT', 'ECE', 'EEE', 'CE', 'MECH', 'H&S', 'MBA'];

        function setStatus(element, message, tone) {
            if (!element) return;
            const iconMap = {
                success: 'fa-check-circle',
                warning: 'fa-exclamation-circle',
                muted: 'fa-cloud'
            };
            element.dataset.tone = tone;
            element.innerHTML = '<i class="fas ' + (iconMap[tone] || iconMap.muted) + '"></i> ' + message;
        }

        function formatSavedTime(isoString) {
            const savedDate = new Date(isoString);
            if (Number.isNaN(savedDate.getTime())) {
                return 'just now';
            }
            return savedDate.toLocaleString();
        }

        function getCsrfToken() {
            if (csrfTokenValue && csrfTokenValue !== 'NOTPROVIDED') {
                return csrfTokenValue;
            }
            const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
            return match ? decodeURIComponent(match[1]) : '';
        }

        function getIndividualTimeTableCards() {
            if (!individualTimeTableContainer) {
                return [];
            }
            return Array.from(individualTimeTableContainer.querySelectorAll('[data-individual-timetable-card]'));
        }

        function getIndividualTimeTableSlots(card) {
            const root = card || individualTimeTableContainer || document;
            return Array.from(root.querySelectorAll('.individual-timetable-slot'));
        }

        function getEmptyTimeTableSlots(card) {
            const root = card || document;
            return Array.from(root.querySelectorAll('.empty-timetable-slot'));
        }

        function getIndividualTimeTableMetaFields(card) {
            const root = card || individualTimeTableContainer || document;
            return Array.from(root.querySelectorAll('.individual-timetable-meta-input'));
        }

        function prepareIndividualTimeTableCard(card, index) {
            if (!card) {
                return null;
            }
            card.querySelectorAll('[id]').forEach(function (element) {
                if (index === 0) {
                    return;
                }
                element.removeAttribute('id');
            });
            getIndividualTimeTableSlots(card).forEach(function (slot) {
                slot.value = '';
            });
            getIndividualTimeTableMetaFields(card).forEach(function (field) {
                field.value = '';
            });
            setTimetableFieldsEditable(card, false);
            return card;
        }

        function ensureIndividualTimeTableCardCount(count) {
            if (!individualTimeTableContainer || !individualTimeTableTemplate) {
                return [];
            }

            const requiredCount = Math.max(count || 1, 1);
            individualTimeTableContainer.innerHTML = '';

            for (let index = 0; index < requiredCount; index += 1) {
                individualTimeTableContainer.appendChild(
                    prepareIndividualTimeTableCard(individualTimeTableTemplate.cloneNode(true), index)
                );
            }

            return getIndividualTimeTableCards();
        }

        function renderSyllabusSubjects(subjects, selectedCode) {
            if (!syllabusSubjectCount || !syllabusSubjectSelect) {
                return;
            }

            syllabusSubjectSelect.innerHTML = '';
            syllabusSubjectCount.textContent = String(subjects.length);

            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Select Subject';
            syllabusSubjectSelect.appendChild(defaultOption);

            if (!subjects.length) {
                return;
            }

            subjects.forEach(function (subject) {
                const option = document.createElement('option');
                option.value = subject.code || '';
                option.dataset.name = subject.name || '';
                option.textContent = getSubjectDisplayLabel(subject.code, subject.name);
                if (selectedCode && option.value === selectedCode) {
                    option.selected = true;
                }
                syllabusSubjectSelect.appendChild(option);

            });
        }

        function renderSubjectSelectionSubjects(subjects, selectedSubject) {
            if (!subjectSelectionFields.subjectName) {
                return;
            }

            const currentSubject = selectedSubject || subjectSelectionFields.subjectName.value || '';
            const selectedBranch = normalizeClassValue(subjectSelectionFields.branch ? subjectSelectionFields.branch.value : '');
            const selectedSection = normalizeClassValue(subjectSelectionFields.section ? subjectSelectionFields.section.value : 'A');
            const selectedYear = normalizeAcademicLevelValue(subjectSelectionFields.year ? subjectSelectionFields.year.value : '');
            const selectedSemester = normalizeAcademicLevelValue(subjectSelectionFields.semester ? subjectSelectionFields.semester.value : '');
            subjectSelectionFields.subjectName.innerHTML = '';

            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Select Subject';
            subjectSelectionFields.subjectName.appendChild(defaultOption);

            subjects.forEach(function (subject) {
                const subjectBranch = normalizeClassValue(subject.branch || '');
                if (subjectBranch && selectedBranch && subjectBranch !== selectedBranch) {
                    return;
                }
                const option = document.createElement('option');
                option.value = subject.name || '';
                option.dataset.code = subject.code || '';
                option.dataset.branch = subject.branch || selectedBranch;
                option.textContent = (subject.code || '-') + ' - ' + (subject.name || '-');
                if (option.value === currentSubject) {
                    option.selected = true;
                }
                subjectSelectionFields.subjectName.appendChild(option);
            });

            if (
                selectedBranch === 'AIML' &&
                selectedYear === '3' &&
                selectedSemester === '1' &&
                ['A', 'B'].includes(selectedSection) &&
                !Array.from(subjectSelectionFields.subjectName.options).some(function (option) {
                    return normalizeSubjectNameForSchedule(option.value) === 'INTERNSHIP';
                })
            ) {
                const internshipOption = document.createElement('option');
                internshipOption.value = 'INTERNSHIP';
                internshipOption.dataset.code = '';
                internshipOption.dataset.branch = selectedBranch;
                internshipOption.textContent = 'INTERNSHIP';
                if (internshipOption.value === currentSubject) {
                    internshipOption.selected = true;
                }
                subjectSelectionFields.subjectName.appendChild(internshipOption);
            }

            if (
                currentSubject &&
                !Array.from(subjectSelectionFields.subjectName.options).some(function (option) {
                    return option.value === currentSubject;
                })
            ) {
                subjectSelectionFields.subjectName.value = '';
            }
        }

        function getSubjectDisplayLabel(subjectCode, subjectName) {
            const code = subjectCode || '-';
            return code + ' - ' + getSubjectShortDisplayName(subjectCode, subjectName);
        }

        function getSubjectShortDisplayName(subjectCode, subjectName) {
            if (normalizeClassValue(subjectCode || '') === '2505305') {
                return 'OOPJ';
            }
            return getShortSubjectLabel(subjectName || '') || subjectName || '-';
        }

        function getBranchLabel(branch) {
            const normalizedBranch = normalizeClassValue(branch);
            if (normalizedBranch === 'AIML') {
                return 'CSE (AI&ML)';
            }
            if (normalizedBranch === 'H&S') {
                return 'H & S';
            }
            return branch;
        }

        function syncSelectOptions(selectElement, values, selectedValue, labelFormatter) {
            if (!selectElement || !Array.isArray(values) || !values.length) {
                return;
            }
            const currentValue = selectedValue || selectElement.value || values[0];
            selectElement.innerHTML = '';
            values.forEach(function (value) {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = labelFormatter ? labelFormatter(value) : value;
                if (String(value) === String(currentValue)) {
                    option.selected = true;
                }
                selectElement.appendChild(option);
            });
            if (!values.map(String).includes(String(currentValue))) {
                selectElement.value = values[0];
            }
        }

        function mergeDepartmentBranches(branches) {
            const seen = new Set();
            return departmentBranches.concat(Array.isArray(branches) ? branches : []).filter(function (branch) {
                const normalizedBranch = normalizeClassValue(branch);
                if (!normalizedBranch || seen.has(normalizedBranch)) {
                    return false;
                }
                seen.add(normalizedBranch);
                return true;
            }).map(function (branch) {
                return normalizeClassValue(branch);
            });
        }

        function syncSubjectSelectionOptions(data) {
            if (!data) {
                return;
            }
            const mergedBranches = mergeDepartmentBranches(data.branches);
            syncSelectOptions(
                subjectSelectionFields.branch,
                mergedBranches,
                data.branch,
                getBranchLabel
            );
            syncSelectOptions(
                timeTableBranchField,
                mergedBranches,
                timeTableBranchField ? timeTableBranchField.value : data.branch,
                getBranchLabel
            );
            syncSelectOptions(
                subjectSelectionFields.year,
                Array.isArray(data.years) ? data.years : [],
                data.year,
                function (year) { return 'Year ' + year; }
            );
            syncSelectOptions(
                subjectSelectionFields.semester,
                Array.isArray(data.semesters) ? data.semesters : [],
                data.semester,
                function (semester) { return 'Semester ' + semester; }
            );
        }

        function normalizeClassValue(value) {
            return String(value || '')
                .trim()
                .toUpperCase()
                .replace('CSE(AI&ML)', 'AIML')
                .replace('CSE (AI&ML)', 'AIML')
                .replace('H & S', 'H&S')
                .replace('H AND S', 'H&S');
        }

        function getLabRoomSuffix(value) {
            const match = String(value || '').match(/\s*\((?:LAB\s*)?ROOM:\s*([^)]+)\)\s*$/i);
            return match ? ' (Room: ' + match[1].trim() + ')' : '';
        }

        function stripLabRoomSuffix(value) {
            return String(value || '').replace(/\s*\((?:LAB\s*)?ROOM:\s*[^)]+\)\s*$/i, '').trim();
        }

        function getComparableSubjectValue(value) {
            return stripLabRoomSuffix(value);
        }

        function normalizeTimeTableDisplayValue(value) {
            const rawValue = String(value || '').trim();
            if (!rawValue) {
                return '';
            }

            const parts = rawValue.split(' - ');
            if (parts.length > 1) {
                const subjectPart = parts.pop();
                const roomSuffix = getLabRoomSuffix(subjectPart);
                return parts.concat(getShortSubjectLabel(stripLabRoomSuffix(subjectPart)) + roomSuffix).join(' - ');
            }

            return getShortSubjectLabel(stripLabRoomSuffix(rawValue)) + getLabRoomSuffix(rawValue);
        }

        function normalizeTimeTableSlotValues(slots) {
            (slots || []).forEach(function (slot) {
                const normalizedValue = normalizeTimeTableDisplayValue(slot.value);
                if (slot.value !== normalizedValue) {
                    slot.value = normalizedValue;
                }
            });
        }

        function normalizeAllTimeTableSlotValues() {
            normalizeTimeTableSlotValues(timeTableSlots);
            normalizeTimeTableSlotValues(getEmptyTimeTableSlots());
            normalizeTimeTableSlotValues(getIndividualTimeTableSlots());
            renderAllTimeTableLoadSummaries();
        }

        function getTimeTableSlotCell(slot) {
            return slot ? slot.closest('td') : null;
        }

        function isVisibleFilledClassSlot(slot) {
            const cell = getTimeTableSlotCell(slot);
            return Boolean(slot && cell && cell.style.display !== 'none' && slot.value.trim());
        }

        function getLoadSummaryType(label) {
            const key = normalizeSubjectNameForSchedule(label);
            if (key === 'SPORTS') {
                return 'Sports';
            }
            if (key === 'LIBRARY') {
                return 'Library';
            }
            if (key === 'MENTORING') {
                return 'Mentoring';
            }
            if (key === 'SEMINAR') {
                return 'Seminar';
            }
            if (key === 'INTERNSHIP' || key === 'INT' || key.indexOf('INTERNSHIP') !== -1) {
                return 'Internship';
            }
            if (isLaboratorySubject(label)) {
                return 'Lab';
            }
            return 'Subject';
        }

        function buildTimeTableLoadSummary(slots) {
            const summary = new Map();
            (slots || []).forEach(function (slot) {
                if (!isVisibleFilledClassSlot(slot)) {
                    return;
                }
                const label = normalizeTimeTableDisplayValue(getComparableSubjectValue(slot.value));
                if (!label) {
                    return;
                }
                const type = getLoadSummaryType(label);
                const key = type + '|' + normalizeSubjectNameForSchedule(label);
                const cell = getTimeTableSlotCell(slot);
                const hours = cell && cell.colSpan && cell.colSpan > 1 ? cell.colSpan : 1;
                if (!summary.has(key)) {
                    summary.set(key, {
                        type: type,
                        label: label,
                        hours: 0
                    });
                }
                summary.get(key).hours += hours;
            });

            const typeOrder = {
                Subject: 1,
                Lab: 2,
                Sports: 3,
                Library: 4,
                Mentoring: 5,
                Internship: 6
            };
            return Array.from(summary.values()).sort(function (first, second) {
                const firstType = typeOrder[first.type] || 99;
                const secondType = typeOrder[second.type] || 99;
                if (firstType !== secondType) {
                    return firstType - secondType;
                }
                return first.label.localeCompare(second.label);
            });
        }

        function renderTimeTableLoadSummary(slots, summaryBody) {
            if (!summaryBody) {
                return;
            }
            const rows = buildTimeTableLoadSummary(slots);
            const totalHours = rows.reduce(function (sum, row) {
                return sum + row.hours;
            }, 0);
            summaryBody.innerHTML = '';
            if (!rows.length) {
                const emptyRow = document.createElement('tr');
                emptyRow.innerHTML = '<td colspan="3" class="text-muted text-center">No timetable hours filled yet.</td>';
                summaryBody.appendChild(emptyRow);
                return;
            }

            rows.forEach(function (row) {
                const tr = document.createElement('tr');
                const typeCell = document.createElement('td');
                const labelCell = document.createElement('td');
                const hoursCell = document.createElement('td');
                typeCell.textContent = row.type;
                labelCell.textContent = row.label;
                hoursCell.textContent = row.hours;
                tr.appendChild(typeCell);
                tr.appendChild(labelCell);
                tr.appendChild(hoursCell);
                summaryBody.appendChild(tr);
            });

            const totalRow = document.createElement('tr');
            totalRow.className = totalHours === 36 ? 'table-success' : 'table-warning';
            const totalLabelCell = document.createElement('th');
            const totalStatusCell = document.createElement('th');
            const totalHoursCell = document.createElement('th');
            totalLabelCell.textContent = 'Total';
            totalStatusCell.textContent = totalHours + ' / 36 hours filled';
            totalHoursCell.textContent = totalHours;
            totalRow.appendChild(totalLabelCell);
            totalRow.appendChild(totalStatusCell);
            totalRow.appendChild(totalHoursCell);
            summaryBody.appendChild(totalRow);
        }

        function renderAllTimeTableLoadSummaries() {
            renderTimeTableLoadSummary(timeTableSlots, document.getElementById('mainTimeTableLoadSummary'));
            emptyTimeTableCards.forEach(function (card) {
                renderTimeTableLoadSummary(
                    getEmptyTimeTableSlots(card),
                    card.querySelector('.empty-timetable-load-summary')
                );
            });
        }

        function getSlotPeriodIndex(slot) {
            return periodOrder.indexOf(slot && slot.dataset ? slot.dataset.period : '');
        }

        function hasSubjectAtPeriod(slots, subjectName, periodIndex, ignoredSlots) {
            const subjectKey = normalizeSubjectNameForSchedule(getComparableSubjectValue(subjectName));
            const ignored = ignoredSlots || new Set();
            return (slots || []).some(function (slot) {
                return !ignored.has(slot) &&
                    isVisibleFilledClassSlot(slot) &&
                    getSlotPeriodIndex(slot) === periodIndex &&
                    normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) === subjectKey;
            });
        }

        function hasSubjectOnDay(slots, subjectName, day, ignoredSlots) {
            const subjectKey = normalizeSubjectNameForSchedule(getComparableSubjectValue(subjectName));
            const ignored = ignoredSlots || new Set();
            return (slots || []).some(function (slot) {
                return !ignored.has(slot) &&
                    isVisibleFilledClassSlot(slot) &&
                    slot.dataset.day === day &&
                    normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) === subjectKey;
            });
        }

        function contextHasOtherLabOnDay(context, day, ignoredSlots) {
            const ignored = ignoredSlots || new Set();
            return (context && context.slots ? context.slots : []).some(function (slot) {
                return !ignored.has(slot) && isVisibleFilledClassSlot(slot) &&
                    slot.dataset.day === day && isLaboratoryScheduleValue(slot.value);
            });
        }

        function getNextClassSlotInRow(slot, slotSelector, includeHidden) {
            const cell = getTimeTableSlotCell(slot);
            const row = cell ? cell.closest('tr') : null;
            if (!cell || !row) {
                return null;
            }
            const cells = Array.from(row.children);
            const nextCell = cells[cells.indexOf(cell) + 1];
            if (!nextCell || nextCell.classList.contains('break-slot') || (!includeHidden && nextCell.style.display === 'none')) {
                return null;
            }
            return nextCell.querySelector(slotSelector || (slot.classList.contains('empty-timetable-slot') ? '.empty-timetable-slot' : '.timetable-slot'));
        }

        function canMoveSubjectToClassSlotWithPreferredSpacing(slots, targetSlot, subjectName, duration, ignoredSlots) {
            return canMoveSubjectToClassSlot(slots, targetSlot, subjectName, duration, ignoredSlots) &&
                !hasSubjectOnDay(slots, subjectName, targetSlot.dataset.day, ignoredSlots);
        }

        function canMoveSubjectToClassSlot(slots, targetSlot, subjectName, duration, ignoredSlots) {
            const targetCell = getTimeTableSlotCell(targetSlot);
            const targetPeriodIndex = getSlotPeriodIndex(targetSlot);
            const ignored = ignoredSlots || new Set();
            if (!targetSlot || !targetCell || targetCell.style.display === 'none' || targetSlot.value.trim()) {
                return false;
            }
            if (targetPeriodIndex < 0 || targetPeriodIndex + duration > periodOrder.length) {
                return false;
            }
            for (let offset = 0; offset < duration; offset += 1) {
                if (hasSubjectAtPeriod(slots, subjectName, targetPeriodIndex + offset, ignored)) {
                    return false;
                }
            }
            if (duration < 2) {
                return true;
            }
            if (![0, 3].includes(targetPeriodIndex)) {
                return false;
            }
            const nextSlot = getNextClassSlotInRow(targetSlot);
            const nextCell = getTimeTableSlotCell(nextSlot);
            return Boolean(nextSlot && nextCell && nextCell.style.display !== 'none' && !nextSlot.value.trim());
        }

        function clearClassSlotValue(slot) {
            const cell = getTimeTableSlotCell(slot);
            const nextSlot = getNextClassSlotInRow(slot, null, true);
            const nextCell = getTimeTableSlotCell(nextSlot);
            if (cell) {
                cell.colSpan = 1;
                cell.classList.remove('lab-merged-cell');
            }
            if (slot) {
                slot.classList.remove('lab-merged-slot');
                slot.value = '';
            }
            if (nextCell && nextCell.style.display === 'none') {
                nextCell.style.display = '';
            }
        }

        function moveClassSlotValue(slots, sourceSlot, targetSlot, slotSelector) {
            const sourceCell = getTimeTableSlotCell(sourceSlot);
            const duration = sourceCell && sourceCell.colSpan > 1 ? sourceCell.colSpan : 1;
            const subjectName = sourceSlot.value.trim();
            const ignoredSlots = new Set([sourceSlot]);
            const sourceNextSlot = duration > 1 ? getNextClassSlotInRow(sourceSlot, slotSelector, true) : null;
            if (sourceNextSlot) {
                ignoredSlots.add(sourceNextSlot);
            }
            if (!canMoveSubjectToClassSlot(slots, targetSlot, subjectName, duration, ignoredSlots)) {
                return false;
            }

            clearClassSlotValue(sourceSlot);
            if (duration > 1) {
                return mergeSlotWithNextPeriod(targetSlot, subjectName, slotSelector);
            }
            targetSlot.value = subjectName;
            return true;
        }

        function repairDuplicateLabDays(context) {
            const slots = context && context.slots ? context.slots : [];
            const daysWithLabs = new Set();
            slots.forEach(function (slot) {
                if (!isVisibleFilledClassSlot(slot) || !isLaboratoryScheduleValue(slot.value)) {
                    return;
                }
                const sourceDay = slot.dataset.day || '';
                if (!sourceDay || !daysWithLabs.has(sourceDay)) {
                    if (sourceDay) {
                        daysWithLabs.add(sourceDay);
                    }
                    return;
                }

                const cell = getTimeTableSlotCell(slot);
                const duration = cell && cell.colSpan > 1 ? cell.colSpan : 2;
                const ignoredSlots = new Set([slot]);
                if (duration > 1) {
                    const nextSlot = getClassSlot(sourceDay, periodOrder[getSlotPeriodIndex(slot) + 1], slots);
                    if (nextSlot) {
                        ignoredSlots.add(nextSlot);
                    }
                }
                const replacementSlot = slots.find(function (candidate) {
                    const targetDay = candidate.dataset.day || '';
                    const targetPeriod = getSlotPeriodIndex(candidate);
                    return targetDay && targetDay !== sourceDay && !daysWithLabs.has(targetDay) &&
                        normalizeClassValue(targetDay) !== 'SAT' && [0, 3].includes(targetPeriod) &&
                        canMoveSubjectToClassSlot(slots, candidate, slot.value, duration, ignoredSlots);
                });
                if (replacementSlot && moveClassSlotValue(slots, slot, replacementSlot, context.slotSelector)) {
                    daysWithLabs.add(replacementSlot.dataset.day || '');
                } else {
                    clearClassSlotValue(slot);
                }
            });
        }

        function repairSameDaySubjectRepeats(slots, slotSelector) {
            const classSlots = slots || [];
            const seenSubjectsByDay = new Map();
            let repairedCount = 0;

            classSlots.forEach(function (slot) {
                if (!isVisibleFilledClassSlot(slot)) {
                    return;
                }

                const subjectKey = normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value));
                const day = slot.dataset.day || '';
                const seenKey = day + '|' + subjectKey;
                if (!subjectKey || !day || !seenSubjectsByDay.has(seenKey)) {
                    seenSubjectsByDay.set(seenKey, slot);
                    return;
                }

                const cell = getTimeTableSlotCell(slot);
                const duration = cell && cell.colSpan > 1 ? cell.colSpan : 1;
                const ignoredSlots = new Set([slot]);
                const nextSlot = duration > 1 ? getNextClassSlotInRow(slot, slotSelector, true) : null;
                if (nextSlot) {
                    ignoredSlots.add(nextSlot);
                }
                const replacementSlot = classSlots.find(function (candidate) {
                    return canMoveSubjectToClassSlotWithPreferredSpacing(
                        classSlots,
                        candidate,
                        slot.value,
                        duration,
                        ignoredSlots
                    );
                });

                if (replacementSlot && moveClassSlotValue(classSlots, slot, replacementSlot, slotSelector)) {
                    repairedCount += 1;
                    return;
                }

                clearClassSlotValue(slot);
                repairedCount += 1;
            });

            return repairedCount;
        }

        function repairSameHourSubjectRepeats(slots, slotSelector) {
            const classSlots = slots || [];
            let repairedCount = 0;

            periodOrder.forEach(function (period, periodIndex) {
                const seenSubjects = new Map();
                classSlots.forEach(function (slot) {
                    if (!isVisibleFilledClassSlot(slot) || getSlotPeriodIndex(slot) !== periodIndex) {
                        return;
                    }

                    const subjectKey = normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value));
                    if (!subjectKey || !seenSubjects.has(subjectKey)) {
                        seenSubjects.set(subjectKey, slot);
                        return;
                    }

                    const replacementSlot = classSlots.find(function (candidate) {
                        return canMoveSubjectToClassSlot(
                            classSlots,
                            candidate,
                            slot.value,
                            getTimeTableSlotCell(slot) && getTimeTableSlotCell(slot).colSpan > 1 ? getTimeTableSlotCell(slot).colSpan : 1,
                            new Set([slot])
                        );
                    });

                    if (replacementSlot && moveClassSlotValue(classSlots, slot, replacementSlot, slotSelector)) {
                        repairedCount += 1;
                        return;
                    }

                    clearClassSlotValue(slot);
                    repairedCount += 1;
                });
            });

            return repairedCount;
        }

        // Direct, selection-based cross-context faculty clash resolver.
        // Builds a subject -> faculty map straight from the user's selections (not from
        // fragile slot-label matching) and ensures no faculty member is booked in two
        // different class contexts at the same day/period (e.g. DM in III-II and COA in
        // II-II both on Monday 1st hour). If a clash is found, one of the entries is moved
        // to a free slot in its own context, or cleared if none is available.
        function resolveCrossContextFacultyClashes(classContexts, selections) {
            return repairAllFacultyConflicts(classContexts, selections);
        }

        function periodsOverlap(leftStart, leftDuration, rightStart, rightDuration) {
            const leftEnd = leftStart + leftDuration - 1;
            const rightEnd = rightStart + rightDuration - 1;
            return leftStart <= rightEnd && rightStart <= leftEnd;
        }

        function getContextLabRoomEntries(contexts, selections) {
            const entries = [];
            const normalizedSelections = normalizeSubjectSelections(selections || getStoredSubjectSelections());

            (contexts || getClassTimeTableContexts(normalizedSelections)).forEach(function (context) {
                const assignments = buildClassAssignments(getSelectionsForClassContext(normalizedSelections, context), context);
                (context.slots || []).forEach(function (slot) {
                    const cell = getTimeTableSlotCell(slot);
                    const assignment = findClassAssignmentByLabel(assignments, getComparableSubjectValue(slot.value));
                    const duration = cell && cell.colSpan > 1 ? cell.colSpan : (assignment && assignment.isLab ? 2 : 1);
                    const labRoomNumber = assignment && assignment.isLab
                        ? (extractLabRoomNumber(slot.value) || assignment.labRoomNumber || getStandardLabRoomNumber(assignment.displayName || assignment.subjectName))
                        : '';
                    const labRoomKey = getLabRoomKey(labRoomNumber) || 'UNASSIGNED';
                    const startPeriodIndex = getSlotPeriodIndex(slot);

                    if (
                        !isVisibleFilledClassSlot(slot) ||
                        !assignment ||
                        !assignment.isLab ||
                        startPeriodIndex < 0
                    ) {
                        return;
                    }

                    entries.push({
                        context: context,
                        slot: slot,
                        subjectName: slot.value.trim(),
                        labRoomKey: labRoomKey,
                        day: slot.dataset.day || '',
                        startPeriodIndex: startPeriodIndex,
                        duration: duration
                    });
                });
            });

            return entries;
        }

        function findLabRoomConflict(entries) {
            const occupied = new Map();
            for (let entryIndex = 0; entryIndex < entries.length; entryIndex += 1) {
                const entry = entries[entryIndex];
                for (let offset = 0; offset < entry.duration; offset += 1) {
                    const key = [entry.labRoomKey, entry.day, entry.startPeriodIndex + offset].join('|');
                    if (occupied.has(key)) {
                        return {
                            existing: occupied.get(key),
                            conflicting: entry
                        };
                    }
                    occupied.set(key, entry);
                }
            }
            return null;
        }

        function targetHasLabRoomConflict(entries, movingEntry, targetSlot) {
            const targetDay = targetSlot.dataset.day || '';
            const targetStartPeriodIndex = getSlotPeriodIndex(targetSlot);
            return entries.some(function (entry) {
                if (entry === movingEntry || entry.slot === movingEntry.slot || entry.labRoomKey !== movingEntry.labRoomKey || entry.day !== targetDay) {
                    return false;
                }
                return periodsOverlap(targetStartPeriodIndex, movingEntry.duration, entry.startPeriodIndex, entry.duration);
            });
        }

        function moveLabRoomConflict(entries, movingEntry) {
            const context = movingEntry.context;
            const ignoredSlots = new Set([movingEntry.slot]);
            const nextSlot = getNextClassSlotInRow(movingEntry.slot, context.slotSelector, true);
            if (nextSlot) {
                ignoredSlots.add(nextSlot);
            }

            const targetSlot = (context.slots || []).find(function (candidate) {
                const periodIndex = getSlotPeriodIndex(candidate);
                return [0, 3].includes(periodIndex) &&
                    normalizeClassValue(candidate.dataset.day) !== 'SAT' &&
                    !contextHasOtherLabOnDay(movingEntry.context, candidate.dataset.day, ignoredSlots) &&
                    canMoveSubjectToClassSlot(context.slots, candidate, movingEntry.subjectName, movingEntry.duration, ignoredSlots) &&
                    !targetHasLabRoomConflict(entries, movingEntry, candidate);
            });

            return Boolean(targetSlot && moveClassSlotValue(context.slots, movingEntry.slot, targetSlot, context.slotSelector));
        }

        function repairAllClassLabRoomConflicts(classContexts, selections) {
            const contexts = classContexts || getClassTimeTableContexts(selections);
            let repairedCount = 0;
            let guard = 0;

            while (guard < 100) {
                guard += 1;
                const entries = getContextLabRoomEntries(contexts, selections);
                const conflict = findLabRoomConflict(entries);
                if (!conflict) {
                    break;
                }
                if (!moveLabRoomConflict(entries, conflict.conflicting)) {
                    clearClassSlotValue(conflict.conflicting.slot);
                }
                repairedCount += 1;
            }

            contexts.forEach(repairDuplicateLabDays);

            return repairedCount;
        }

        function getContextFacultyEntries(classContexts, selections) {
            const entries = [];
            const normalizedSelections = normalizeSubjectSelections(selections || getStoredSubjectSelections());
            (classContexts || getClassTimeTableContexts()).forEach(function (context) {
                const contextSelections = getSelectionsForClassContext(normalizedSelections, context);
                const assignments = buildClassAssignments(contextSelections, context);
                (context.slots || []).forEach(function (slot) {
                    if (!isVisibleFilledClassSlot(slot)) {
                        return;
                    }
                    const value = (slot.value || '').trim();
                    const comparableValue = getComparableSubjectValue(value);
                    const assignment = findClassAssignmentByLabel(assignments, comparableValue);
                    if (!assignment || !assignment.facultyKey) {
                        return;
                    }
                    const day = slot.dataset.day || '';
                    const periodIndex = getSlotPeriodIndex(slot);
                    const cell = getTimeTableSlotCell(slot);
                    const duration = cell && cell.colSpan > 1 ? cell.colSpan : (assignment.isLab ? 2 : 1);

                    if (day && periodIndex >= 0) {
                        entries.push({
                            slot: slot,
                            context: context,
                            facultyKey: assignment.facultyKey,
                            comparableValue: comparableValue,
                            isLab: assignment.isLab,
                            day: day,
                            periodIndex: periodIndex,
                            duration: duration
                        });
                    }
                });
            });

            return entries;
        }

        function findFacultyConflict(entries) {
            const byFaculty = new Map();
            for (let entryIndex = 0; entryIndex < entries.length; entryIndex += 1) {
                const entry = entries[entryIndex];
                if (!byFaculty.has(entry.facultyKey)) {
                    byFaculty.set(entry.facultyKey, []);
                }
                byFaculty.get(entry.facultyKey).push(entry);
            }

            for (const [facultyKey, facultyEntries] of byFaculty) {
                for (let i = 0; i < facultyEntries.length; i += 1) {
                    for (let j = i + 1; j < facultyEntries.length; j += 1) {
                        const a = facultyEntries[i];
                        const b = facultyEntries[j];
                        if (a.day !== b.day) {
                            continue;
                        }
                        const aStart = a.periodIndex;
                        const aEnd = a.periodIndex + a.duration - 1;
                        const bStart = b.periodIndex;
                        const bEnd = b.periodIndex + b.duration - 1;
                        if (periodsOverlap(aStart, a.duration, bStart, b.duration)) {
                            return { first: a, second: b };
                        }
                    }
                }
            }

            return null;
        }

        function repairAllFacultyConflicts(classContexts, selections) {
            const contexts = classContexts || getClassTimeTableContexts();
            let repairedCount = 0;
            let guard = 0;

            while (guard < 100) {
                guard += 1;
                const entries = getContextFacultyEntries(contexts, selections);
                const conflict = findFacultyConflict(entries);
                if (!conflict) {
                    break;
                }

                const conflictingEntry = conflict.second;
                const context = conflictingEntry.context;
                const slotSelector = context.slotSelector || '.timetable-slot';

                const ignoredSlots = new Set([conflictingEntry.slot]);
                if (conflictingEntry.duration > 1) {
                    const nextSlot = getClassSlot(conflictingEntry.day, periodOrder[conflictingEntry.periodIndex + 1], context.slots);
                    if (nextSlot) {
                        ignoredSlots.add(nextSlot);
                    }
                }

                const targetSlot = (context.slots || []).find(function (candidate) {
                    const cell = getTimeTableSlotCell(candidate);
                    if (!cell || cell.style.display === 'none' || candidate.value.trim() || ignoredSlots.has(candidate)) {
                        return false;
                    }
                    const targetPeriod = getSlotPeriodIndex(candidate);
                    const targetDay = candidate.dataset.day || '';
                    const duration = conflictingEntry.duration;
                    if (targetPeriod < 0 || targetPeriod + duration > periodOrder.length) {
                        return false;
                    }
                    if (duration > 1) {
                        if (![0, 3].includes(targetPeriod)) {
                            return false;
                        }
                        const nextSlot = getClassSlot(targetDay, periodOrder[targetPeriod + 1], context.slots);
                        const nextCell = nextSlot ? getTimeTableSlotCell(nextSlot) : null;
                        if (!nextSlot || !nextCell || nextCell.style.display === 'none' || nextSlot.value.trim()) {
                            return false;
                        }
                    }
                    if (normalizeClassValue(targetDay) === 'SAT' && duration > 1) {
                        return false;
                    }
                    if (conflictingEntry.isLab &&
                        contextHasOtherLabOnDay(context, targetDay, ignoredSlots)) {
                        return false;
                    }

                    const otherEntries = entries.filter(function (e) {
                        return e.facultyKey === conflictingEntry.facultyKey && e !== conflictingEntry;
                    });
                    const occupiedPeriods = new Set();
                    otherEntries.forEach(function (e) {
                        if (e.day !== targetDay) {
                            return;
                        }
                        for (let offset = 0; offset < e.duration; offset += 1) {
                            occupiedPeriods.add(e.periodIndex + offset);
                        }
                    });
                    for (let offset = 0; offset < duration; offset += 1) {
                        if (occupiedPeriods.has(targetPeriod + offset)) {
                            return false;
                        }
                    }
                    return true;
                });

                if (targetSlot) {
                    moveClassSlotValue(context.slots, conflictingEntry.slot, targetSlot, slotSelector);
                } else {
                    clearClassSlotValue(conflictingEntry.slot);
                }
                repairedCount += 1;
            }

            contexts.forEach(repairDuplicateLabDays);

            return repairedCount;
        }

        function repairAllTimetableResourceConflicts(classContexts, selections) {
            const contexts = classContexts || getClassTimeTableContexts(selections || getStoredSubjectSelections());
            const summary = { faculty: 0, labRoom: 0 };
            for (let pass = 0; pass < 3; pass += 1) {
                const facultyRepairs = repairAllFacultyConflicts(contexts, selections);
                const labRoomRepairs = repairAllClassLabRoomConflicts(contexts, selections);
                summary.faculty += facultyRepairs;
                summary.labRoom += labRoomRepairs;
                if (!facultyRepairs && !labRoomRepairs) {
                    break;
                }
            }
            return summary;
        }

        function annotateClassLabRoomNumbers(classContexts, selections) {
            const normalizedSelections = normalizeSubjectSelections(selections || getStoredSubjectSelections());
            let annotatedCount = 0;

            (classContexts || getClassTimeTableContexts(normalizedSelections)).forEach(function (context) {
                const assignments = buildClassAssignments(getSelectionsForClassContext(normalizedSelections, context), context);
                (context.slots || []).forEach(function (slot) {
                    if (!isVisibleFilledClassSlot(slot) || !isLaboratoryScheduleValue(slot.value)) {
                        return;
                    }
                    const assignment = findClassAssignmentByLabel(assignments, getComparableSubjectValue(slot.value));
                    if (!assignment || !assignment.isLab) {
                        return;
                    }
                    const nextValue = getAssignmentSlotDisplayName(assignment);
                    if (nextValue && slot.value !== nextValue) {
                        slot.value = nextValue;
                        annotatedCount += 1;
                    }
                });
            });

            return annotatedCount;
        }

         function repairAllClassTimeTableSameHourRepeats(classContexts) {
             let total = 0;
             (classContexts || []).forEach(function (context) {
                 if (!context || !context.slots) {
                     return;
                 }
                 const slots = context.slots;
                 for (let periodIndex = 0; periodIndex < periodOrder.length; periodIndex += 1) {
                     const period = periodOrder[periodIndex];
                     const subjectDayMap = new Map();
                     slots.forEach(function (slot) {
                         if (slot.dataset.period !== period || !isVisibleFilledClassSlot(slot)) {
                             return;
                         }
                         const value = slot.value.trim();
                         const key = normalizeSubjectNameForSchedule(getComparableSubjectValue(value));
                         if (isLaboratoryScheduleValue(value) || key === 'SPORTS' || timetableActivityOrder.has(key)) {
                             return;
                         }
                         if (!subjectDayMap.has(key)) {
                             subjectDayMap.set(key, []);
                         }
                         subjectDayMap.get(key).push(slot);
                     });
                     subjectDayMap.forEach(function (slotList, key) {
                         if (slotList.length <= 1) {
                             return;
                         }
                         for (let index = 1; index < slotList.length; index += 1) {
                             const sourceSlot = slotList[index];
                             const day = sourceSlot.dataset.day;
                             const targetSlot = slots.find(function (candidate) {
                                 return candidate.dataset.day === day &&
                                     getSlotPeriodIndex(candidate) >= 0 &&
                                     candidate !== sourceSlot &&
                                     !candidate.value.trim() &&
                                     canMoveSubjectToClassSlotWithPreferredSpacing(slots, candidate, sourceSlot.value.trim(), 1, new Set([sourceSlot]));
                             });
                             if (targetSlot && moveClassSlotValue(slots, sourceSlot, targetSlot, context.slotSelector || '.timetable-slot')) {
                                 total += 1;
                             }
                         }
                     });
                 }
             });
             return total;
         }

         function applyTimeTableRequirementRepairs(classContexts, selections) {
             const normalizedSelections = normalizeSubjectSelections(selections || getStoredSubjectSelections());
             const contexts = classContexts || getClassTimeTableContexts(normalizedSelections);
             const facultyOccupancyMap = createFacultyOccupancyMap();
             const labRoomOccupancyMap = createLabRoomOccupancyMap();
             prePopulateOccupancyMapsFromExistingData(facultyOccupancyMap, labRoomOccupancyMap);
             const summary = {
                 sameHourRepeats: 0,
                 labRoomConflicts: 0,
                 facultyConflicts: 0,
                 filledBlankSlots: 0,
                 addedAIMLOSLab: 0,
                 fixedLayouts: 0,
                 projectStageLabs: 0,
                 movedActivities: 0,
                 annotatedLabRooms: 0,
                 mergedLabRepairs: 0,
                 total: 0
             };

             summary.sameHourRepeats += repairAllClassTimeTableSameHourRepeats(contexts);
             summary.facultyConflicts += repairAllFacultyConflicts(contexts, normalizedSelections);
             summary.labRoomConflicts += repairAllClassLabRoomConflicts(contexts, normalizedSelections);
             summary.fixedLayouts += ensureFixedRequiredLayouts(contexts);
             const freshFacultyOccupancyMap = createFacultyOccupancyMap();
             const freshLabRoomOccupancyMap = createLabRoomOccupancyMap();
             prePopulateOccupancyMapsFromExistingData(freshFacultyOccupancyMap, freshLabRoomOccupancyMap);
             summary.filledBlankSlots += fillAllClassBlankSlots(contexts, normalizedSelections, freshFacultyOccupancyMap, freshLabRoomOccupancyMap);
              summary.addedAIMLOSLab += ensureR25TwoOneAIMLCompletePlans();
             summary.filledBlankSlots += fillAllClassBlankSlots(contexts, normalizedSelections, freshFacultyOccupancyMap, freshLabRoomOccupancyMap);
             summary.labRoomConflicts += repairAllClassLabRoomConflicts(contexts, normalizedSelections);
             summary.facultyConflicts += repairAllFacultyConflicts(classContexts, normalizedSelections);
              summary.movedActivities += enforceActivitiesLastHours(contexts);
              (contexts || []).forEach(function (context) {
                  const y = normalizeAcademicLevelValue(context.year);
                  if (y === '2' || y === '3') {
                      summary.movedActivities += ensureSportsBlock(context);
                  }
              });
              summary.annotatedLabRooms += annotateClassLabRoomNumbers(contexts, normalizedSelections);
             summary.labRoomConflicts += repairAllClassLabRoomConflicts(classContexts, normalizedSelections);
             summary.facultyConflicts += repairAllFacultyConflicts(classContexts, normalizedSelections);
             summary.filledBlankSlots += fillAllClassBlankSlots(contexts, normalizedSelections, freshFacultyOccupancyMap, freshLabRoomOccupancyMap);
             summary.mergedLabRepairs += repairR22ThreeTwoITSELabEntries(contexts);
             const finalResourceRepairs = repairAllTimetableResourceConflicts(contexts, normalizedSelections);
             summary.labRoomConflicts += finalResourceRepairs.labRoom;
             summary.facultyConflicts += finalResourceRepairs.faculty;
             summary.total = summary.sameHourRepeats +
                 summary.labRoomConflicts +
                 summary.facultyConflicts +
                 summary.filledBlankSlots +
                 summary.addedAIMLOSLab +
                 summary.fixedLayouts +
                 summary.projectStageLabs +
                 summary.movedActivities +
                 summary.annotatedLabRooms +
                 summary.mergedLabRepairs;

             return summary;
         }

         function fillClassBlankSlots(context, classSelections, facultyOccupancyMap, labRoomOccupancyMap) {
             const assignments = buildClassAssignments(classSelections, context);
             const subjectPeriodUsageMap = createSubjectPeriodUsageMap();
             const labDaysUsed = new Set();
             const days = Array.from(new Set((context.slots || []).map(function (slot) {
                 return slot.dataset.day || '';
             }).filter(Boolean)));
             let filledCount = 0;

             const freshFacultyMap = createFacultyOccupancyMap();
             const freshLabRoomMap = createLabRoomOccupancyMap();

             (context.slots || []).forEach(function (slot) {
                 const slotValue = (slot.value || '').trim();
                 if (!slotValue) {
                     return;
                 }
                 const comparableValue = getComparableSubjectValue(slotValue);
                 const assignment = findClassAssignmentByLabel(assignments, comparableValue);
                 if (!assignment) {
                     return;
                 }
                 const day = slot.dataset.day || '';
                 if (assignment.isLab && day) {
                     labDaysUsed.add(day);
                 }
                 const periodIndex = periodOrder.indexOf(slot.dataset.period || '');
                  const isSlotSports = (assignment.subjectName || '').toUpperCase() === 'SPORTS';
                  const duration = getTimeTableSlotCell(slot) && slot.closest('td').colSpan > 1 ? slot.closest('td').colSpan : (assignment.isLab ? 2 : (isSlotSports && getSportsDurationForContext(context) === 2 ? 2 : 1));
                 if (day && periodIndex >= 0) {
                     reserveSubjectPeriods(subjectPeriodUsageMap, assignment, periodIndex, duration);
                     if (assignment.isLab) {
                         const labRoomLabel = slotValue.match(/\((?:LAB\s*)?ROOM:\s*([^)]+)\)/i);
                         const labRoomNumber = (labRoomLabel ? labRoomLabel[1] : '') || assignment.labRoomNumber || getStandardLabRoomNumber(comparableValue);
                         const labAssignment = Object.assign({}, assignment, { labRoomNumber: labRoomNumber });
                         reserveLabRoomPeriods(freshLabRoomMap, labAssignment, day, periodIndex, duration);
                     }
                     reserveFacultyPeriods(freshFacultyMap, assignment.facultyKey, day, periodIndex, duration);
                 }
             });

             function refreshPlacedHours() {
                 assignments.forEach(function (assignment) {
                     assignment.placedHours = countClassAssignmentHours(context, assignment);
                 });
             }

              function findBlankTarget(day, assignment, strictSpacing) {
                  if (!assignment) {
                      return null;
                  }
                  if (assignment.isLab && labDaysUsed.has(day)) {
                      return null;
                  }
                  const duration = assignment.isLab ? 2 : ((assignment.subjectName || '').toUpperCase() === 'SPORTS' && getSportsDurationForContext(context) === 2 ? 2 : 1);
                 return (context.slots || []).find(function (slot) {
                     const periodIndex = getSlotPeriodIndex(slot);
                     const cell = getTimeTableSlotCell(slot);
                     if (!cell || cell.style.display === 'none' || slot.value.trim() || slot.dataset.day !== day) {
                         return false;
                     }
                     if (duration > 1) {
                         const nextSlot = getClassSlot(day, periodOrder[periodIndex + 1], context.slots);
                         const nextCell = getTimeTableSlotCell(nextSlot);
                         if (![0, 3].includes(periodIndex) || normalizeClassValue(day) === 'SAT') {
                             return false;
                         }
                         if (!nextSlot || !nextCell || nextCell.classList.contains('break-slot') || nextCell.style.display === 'none' || nextSlot.value.trim()) {
                             return false;
                         }
                     }
                     if (hasFacultyConflict(freshFacultyMap, assignment.facultyKey, day, periodIndex, duration)) {
                         return false;
                     }
                     if (hasLabRoomPeriodConflict(freshLabRoomMap, assignment, day, periodIndex, duration)) {
                         return false;
                     }
                     if (strictSpacing && !assignment.isActivity && contextHasAssignmentOnDay(context, assignment, day)) {
                         return false;
                     }
                     return true;
                 });
             }

              function placeAssignmentInSlot(assignment, slot) {
                  if (!assignment || !slot) {
                      return false;
                  }
                  const duration = assignment.isLab ? 2 : ((assignment.subjectName || '').toUpperCase() === 'SPORTS' && getSportsDurationForContext(context) === 2 ? 2 : 1);
                 if (duration > 1) {
                     if (!mergeSlotWithNextPeriod(slot, getAssignmentSlotDisplayName(assignment), context.slotSelector)) {
                         return false;
                     }
                 } else {
                     slot.value = getAssignmentSlotDisplayName(assignment);
                 }
                 const day = slot.dataset.day || '';
                 const periodIndex = periodOrder.indexOf(slot.dataset.period || '');
                 reserveSubjectPeriods(subjectPeriodUsageMap, assignment, periodIndex, duration);
                 if (assignment.isLab) {
                     const labRoomNumber = assignment.labRoomNumber || getStandardLabRoomNumber(assignment.displayName || assignment.subjectName);
                     reserveLabRoomPeriods(freshLabRoomMap, assignment, day, periodIndex, duration);
                     labDaysUsed.add(day);
                 }
                 reserveFacultyPeriods(freshFacultyMap, assignment.facultyKey, day, periodIndex, duration);
                 assignment.placedHours += duration;
                 filledCount += duration;
                 return true;
             }

             [true, false].forEach(function (strictSpacing) {
                 let guard = 0;
                 let placed = true;
                 while (placed && guard < 100) {
                     guard += 1;
                     placed = false;
                     refreshPlacedHours();
                      assignments.some(function (assignment, assignmentIndex) {
                          if (!assignment) {
                              return false;
                          }
                          const duration = assignment.isLab ? 2 : ((assignment.subjectName || '').toUpperCase() === 'SPORTS' && getSportsDurationForContext(context) === 2 ? 2 : 1);
                          if (assignment.placedHours + duration > assignment.targetHours) {
                              return false;
                          }
                         return days.some(function (day, dayOffset) {
                             const targetDay = days[(assignmentIndex + dayOffset) % days.length];
                             const targetSlot = findBlankTarget(targetDay, assignment, strictSpacing);
                             if (!targetSlot) {
                                 return false;
                             }
                             placed = placeAssignmentInSlot(assignment, targetSlot);
                             return placed;
                         });
                     });
                 }
             });

             return filledCount;
         }

          function fillAllClassBlankSlots(classContexts, selections, facultyOccupancyMap, labRoomOccupancyMap) {
              const normalizedSelections = normalizeSubjectSelections(selections || getStoredSubjectSelections());
              return (classContexts || getClassTimeTableContexts(normalizedSelections)).reduce(function (total, context) {
                  const contextSelections = getSelectionsForClassContext(normalizedSelections, context);
                  const trimmedHours = trimR25TwoTwoITHoursToTargets(context, contextSelections) +
                      trimR22ThreeTwoITTheoryHoursToTargets(context, contextSelections);
                  return total + trimmedHours + fillClassBlankSlots(context, contextSelections, facultyOccupancyMap, labRoomOccupancyMap);
              }, 0);
          }

          function trimR22ThreeTwoITTheoryHoursToTargets(context, selections) {
              if (!isR22ThreeTwoITContext(context)) {
                  return 0;
              }
              const assignments = buildClassAssignments(selections, context).filter(function (assignment) {
                  return !assignment.isLab && !assignment.isActivity;
              });
              let removedHours = 0;
              const subjectKeys = new Set();
              function getTheorySubjectKey(value) {
                  const assignment = findClassAssignmentByLabel(assignments, value);
                  return normalizeSubjectNameForSchedule(assignment ? assignment.displayName : value);
              }
              (context.slots || []).forEach(function (slot) {
                  if (!isVisibleFilledClassSlot(slot)) {
                      return;
                  }
                  const value = getComparableSubjectValue(slot.value);
                  const normalizedValue = normalizeSubjectNameForSchedule(value);
                  if (isLaboratoryScheduleValue(value) || normalizedValue === 'SPORTS' || timetableActivityOrder.has(normalizedValue)) {
                      return;
                  }
                  subjectKeys.add(getTheorySubjectKey(value));
              });
              subjectKeys.forEach(function (subjectKey) {
                  let currentHours = 0;
                  const matchingSlots = (context.slots || []).filter(function (slot) {
                      return isVisibleFilledClassSlot(slot) && getTheorySubjectKey(getComparableSubjectValue(slot.value)) === subjectKey;
                  }).sort(function (left, right) {
                      const dayOrder = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
                      const dayDifference = dayOrder.indexOf(right.dataset.day) - dayOrder.indexOf(left.dataset.day);
                      return dayDifference || getSlotPeriodIndex(right) - getSlotPeriodIndex(left);
                  });
                  currentHours = matchingSlots.reduce(function (total, slot) {
                      const cell = getTimeTableSlotCell(slot);
                      return total + (cell && cell.colSpan > 1 ? cell.colSpan : 1);
                  }, 0);
                  matchingSlots.forEach(function (slot) {
                      if (currentHours <= 5) {
                          return;
                      }
                      const cell = getTimeTableSlotCell(slot);
                      const duration = cell && cell.colSpan > 1 ? cell.colSpan : 1;
                      clearClassSlotValue(slot);
                      currentHours -= duration;
                      removedHours += duration;
                  });
              });
              return removedHours;
          }

          function repairR22ThreeTwoITSELabEntries(contexts) {
              let repaired = 0;
              const canonicalValue = 'SE Lab (Room: D-314)';
              const dayOrder = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
              function isSELabRoomValue(value) {
                  const roomMatch = String(value || '').match(/\(\s*ROOM:\s*([^)]+)\)/i);
                  const label = normalizeSubjectNameForSchedule(getComparableSubjectValue(value)).split(' - ').pop().trim();
                  return Boolean(roomMatch) && normalizeClassValue(roomMatch[1]) === 'D-314' &&
                      (label === 'SE' || label === 'SE LAB');
              }
              (contexts || []).forEach(function (context) {
                  if (!isR22ThreeTwoITContext(context)) {
                      return;
                  }
                  const slots = context.slots || [];
                  const entries = slots.filter(function (slot) {
                      return isVisibleFilledClassSlot(slot) && isSELabRoomValue(slot.value);
                  }).sort(function (left, right) {
                      const leftPeriod = getSlotPeriodIndex(left);
                      const rightPeriod = getSlotPeriodIndex(right);
                      const leftIsMergedStart = [0, 3].includes(leftPeriod) && getTimeTableSlotCell(left).colSpan > 1;
                      const rightIsMergedStart = [0, 3].includes(rightPeriod) && getTimeTableSlotCell(right).colSpan > 1;
                      if (leftIsMergedStart !== rightIsMergedStart) {
                          return leftIsMergedStart ? -1 : 1;
                      }
                      const leftIsStart = [0, 3].includes(leftPeriod);
                      const rightIsStart = [0, 3].includes(rightPeriod);
                      if (leftIsStart !== rightIsStart) {
                          return leftIsStart ? -1 : 1;
                      }
                      return dayOrder.indexOf(left.dataset.day) - dayOrder.indexOf(right.dataset.day) || leftPeriod - rightPeriod;
                  });
                  if (!entries.length) {
                      return;
                  }

                  const keep = entries[0];
                  entries.slice(1).forEach(function (duplicate) {
                      clearClassSlotValue(duplicate);
                      repaired += 1;
                  });
                  if (keep.value.trim() !== canonicalValue) {
                      keep.value = canonicalValue;
                      repaired += 1;
                  }
                  const keepCell = getTimeTableSlotCell(keep);
                  if (keepCell && keepCell.colSpan > 1) {
                      return;
                  }

                  function canMergeAt(startSlot) {
                      if (!startSlot || normalizeClassValue(startSlot.dataset.day) === 'SAT') {
                          return false;
                      }
                      const periodIndex = getSlotPeriodIndex(startSlot);
                      if (![0, 3].includes(periodIndex)) {
                          return false;
                      }
                      const nextSlot = getClassSlot(startSlot.dataset.day, periodOrder[periodIndex + 1], slots);
                      const startValue = startSlot.value.trim();
                      const nextValue = nextSlot ? nextSlot.value.trim() : '';
                      const startCell = getTimeTableSlotCell(startSlot);
                      const nextCell = nextSlot ? getTimeTableSlotCell(nextSlot) : null;
                      return Boolean(startCell && nextCell) &&
                          startCell.style.display !== 'none' &&
                          nextCell.style.display !== 'none' &&
                          (!startValue || isSELabRoomValue(startValue)) &&
                          (!nextValue || isSELabRoomValue(nextValue));
                  }

                  let startSlot = [0, 3].includes(getSlotPeriodIndex(keep)) ? keep : null;
                  if (getSlotPeriodIndex(keep) === 4) {
                      const previousSlot = getClassSlot(keep.dataset.day, periodOrder[3], slots);
                      if (canMergeAt(previousSlot)) {
                          startSlot = previousSlot;
                      }
                  }
                  if (!canMergeAt(startSlot)) {
                      startSlot = null;
                      dayOrder.some(function (day) {
                          return [3, 0].some(function (periodIndex) {
                              const candidate = getClassSlot(day, periodOrder[periodIndex], slots);
                              if (!canMergeAt(candidate)) {
                                  return false;
                              }
                              startSlot = candidate;
                              return true;
                          });
                      });
                  }
                  if (!startSlot) {
                      return;
                  }
                  if (startSlot !== keep) {
                      const displacedValues = [startSlot, getClassSlot(startSlot.dataset.day, periodOrder[getSlotPeriodIndex(startSlot) + 1], slots)]
                          .map(function (slot) { return slot ? slot.value.trim() : ''; })
                          .filter(function (value) { return value && !isSELabRoomValue(value); });
                      if (displacedValues.length) {
                          return;
                      }
                      clearClassSlotValue(keep);
                  }
                  if (mergeSlotWithNextPeriod(startSlot, canonicalValue, context.slotSelector)) {
                      repaired += 1;
                  }
              });
              return repaired;
          }

          function trimR25TwoTwoITHoursToTargets(context, selections) {
              if (!isR25TwoTwoITContext(context)) {
                  return 0;
              }
              const assignments = buildClassAssignments(selections, context);
              let removedHours = 0;
              assignments.forEach(function (assignment) {
                  let currentHours = countClassAssignmentHours(context, assignment);
                  if (currentHours <= assignment.targetHours) {
                      return;
                  }
                  const matchingSlots = (context.slots || []).filter(function (slot) {
                      return isVisibleFilledClassSlot(slot) &&
                          normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) ===
                          normalizeSubjectNameForSchedule(assignment.displayName);
                  }).sort(function (left, right) {
                      const dayOrder = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
                      const dayDifference = dayOrder.indexOf(right.dataset.day) - dayOrder.indexOf(left.dataset.day);
                      return dayDifference || getSlotPeriodIndex(right) - getSlotPeriodIndex(left);
                  });
                  matchingSlots.forEach(function (slot) {
                      if (currentHours <= assignment.targetHours) {
                          return;
                      }
                      const cell = getTimeTableSlotCell(slot);
                      const duration = cell && cell.colSpan > 1 ? cell.colSpan : 1;
                      clearClassSlotValue(slot);
                      currentHours -= duration;
                      removedHours += duration;
                  });
              });
              return removedHours;
          }

        function applyFixedDisplayPlan(context, plan) {
            resetClassTimeTableMerges(context.slots);
            context.slots.forEach(function (slot) {
                slot.value = '';
            });

            Object.keys(plan).forEach(function (day) {
                plan[day].forEach(function (label, periodIndex) {
                    if (!label) {
                        return;
                    }
                    const slot = getClassSlot(day, periodOrder[periodIndex], context.slots);
                    if (!slot) {
                        return;
                    }
                    if (isLaboratoryScheduleValue(label) || (normalizeSubjectNameForSchedule(label) === 'SPORTS' && getSportsDurationForContext(context) === 2)) {
                        if (!mergeSlotWithNextPeriod(slot, label, context.slotSelector)) {
                            slot.value = label;
                        }
                        return;
                    }
                    slot.value = label;
                });
            });

            return true;
        }

        function applyFixedPlanToSlots(slots, slotSelector, plan) {
            const context = {
                slots: slots || [],
                slotSelector: slotSelector || '.empty-timetable-slot'
            };
            return applyFixedDisplayPlan(context, plan);
        }

        function getRequiredFixedPlanForSpec(regulation, year, semester, branch, section) {
            const key = [
                normalizeClassValue(regulation || 'R22'),
                normalizeAcademicLevelValue(year),
                normalizeAcademicLevelValue(semester),
                normalizeClassValue(branch),
                getSectionContextValue(section, branch)
            ].join('|');
             const plans = {
                 'R25|2|1|AIML|A': {
                     MON: ['COA', 'OOPJ', 'SE', 'CM Lab', 'OOPJ', 'DBMS'],
                     TUE: ['MSF', 'COA', 'OOPJ', 'Java Lab', 'SE', 'SE'],
                     WED: ['SE Lab', 'DBMS', 'DBMS', 'MSF', 'COA', 'OOPJ'],
                     THU: ['DBMS Lab', 'SE', 'SE', 'DBMS', 'MSF', 'VEGS'],
                     FRI: ['NODE JS Lab', 'COA', 'COA', 'OOPJ', 'SPORTS', 'SE'],
                     SAT: ['SE', 'DBMS', 'VEGS', 'MSF', 'LIBRARY', 'MENTORING']
                 },
                 'R25|2|1|AIML|B': {
                     MON: ['CM Lab', 'OOPJ', 'COA', 'OOPJ', 'SE', 'DBMS'],
                     TUE: ['Java Lab', 'SE', 'COA', 'OOPJ', 'SE', 'DBMS'],
                     WED: ['SE Lab', 'DBMS', 'COA', 'OOPJ', 'SE', 'MSF'],
                     THU: ['DBMS Lab', 'MSF', 'COA', 'OOPJ', 'SE', 'VEGS'],
                     FRI: ['NODE JS Lab', 'COA', 'DBMS', 'MSF', 'SPORTS', 'SE'],
                     SAT: ['COA', 'MSF', 'VEGS', 'MSF', 'LIBRARY', 'MENTORING']
                 },
                  'R25|2|1|IT|': {
                      MON: ['CM Lab', 'OOPJ', 'IoT', 'OOPJ', 'OS', 'COA'],
                      TUE: ['Java Lab', 'OS', 'MSF', 'COA', 'OOPJ', 'OS'],
                      WED: ['OS Lab', 'COA', 'IoT', 'MSF', 'COA', 'OOPJ'],
                      THU: ['IoT Lab', 'MSF', 'OS', 'IoT', 'MSF', 'EVS/IKS'],
                       FRI: ['DV Lab', 'COA', 'OOPJ', 'OS', 'SPORTS', 'IoT'],
                      SAT: ['MSF', 'EVS/IKS', 'MENTORING', 'LIBRARY', 'OS', 'IoT']
                  },
                  'R22|2|1|IT|': {
                      MON: ['CM Lab', 'OOPJ', 'OS', 'OOPJ', 'IoT', 'COA'],
                      TUE: ['Java Lab', 'COA', 'MSF', 'OOPJ', 'OS', 'IoT'],
                      WED: ['OS Lab', 'IoT', 'COA', 'MSF', 'OOPJ', 'OS'],
                      THU: ['IoT Lab', 'MSF', 'OOPJ', 'IoT', 'MSF', 'EVS/IKS'],
                      FRI: ['DV Lab', 'COA', 'OS', 'IoT', 'SPORTS', 'OOPJ'],
                      SAT: ['MSF', 'EVS/IKS', 'MENTORING', 'LIBRARY', 'COA', 'OS']
                  },
                  'R22|2|1|AIML|A': {
                      MON: ['ML Lab', 'OOPJ', 'OS', 'OOPJ', 'IoT', 'COA'],
                      TUE: ['Java Lab', 'COA', 'MSF', 'OOPJ', 'OS', 'IoT'],
                      WED: ['OS Lab', 'IoT', 'COA', 'MSF', 'OOPJ', 'OS'],
                      THU: ['IoT Lab', 'MSF', 'OOPJ', 'IoT', 'MSF', 'VEGS'],
                      FRI: ['DA Lab', 'COA', 'OS', 'IoT', 'SPORTS', 'OOPJ'],
                      SAT: ['MSF', 'VEGS', 'MENTORING', 'LIBRARY', 'COA', 'OS']
                  },
                 'R22|3|1|AIML|A': {
                     MON: ['ML Lab', 'ML', 'ML', 'CN', 'DL', 'NLP'],
                     TUE: ['CN Lab', 'DA', 'ML', 'CN', 'DL', 'NLP'],
                     WED: ['NLP Lab', 'NLP', 'DA', 'ML', 'CN', 'DL'],
                     THU: ['DA Lab', 'DL', 'NLP', 'DA', 'NLP', 'MENTORING'],
                     FRI: ['ML', 'CN', 'DL', 'NLP', 'DA', 'SPORTS'],
                     SAT: ['ML', 'CN', 'DL', 'NLP', 'DA', 'LIBRARY']
                 },
                 'R22|3|1|AIML|B': {
                     MON: ['ML', 'CN', 'DL', 'ML Lab', 'DA', 'NLP'],
                     TUE: ['DA', 'ML', 'CN', 'CN Lab', 'ML', 'DL'],
                     WED: ['NLP', 'DA', 'ML', 'NLP Lab', 'NLP', 'CN'],
                     THU: ['DL', 'NLP', 'DA', 'DA Lab', 'DL', 'MENTORING'],
                     FRI: ['ML', 'CN', 'DL', 'NLP', 'DA', 'SPORTS'],
                     SAT: ['ML', 'CN', 'DL', 'NLP', 'DA', 'LIBRARY']
                 },
                 'R22|3|1|IT|': {
                     MON: ['CD Lab', 'DDB', 'DAA', 'ACD', 'ES', 'DM'],
                      TUE: ['Data Mining Lab', 'DAA', 'DDB', 'DAA', 'ACD', 'ES'],
                     WED: ['ES Lab', 'ACD', 'DM', 'DDB', 'DAA', 'ACD'],
                     THU: ['DAA', 'DM', 'ES', 'Flutter Lab', 'DM', 'MENTORING'],
                     FRI: ['ES', 'DAA', 'ACD', 'DM', 'DDB', 'SPORTS'],
                     SAT: ['ACD', 'DDB', 'DM', 'ES', 'DDB', 'LIBRARY']
                 },
                  'R22|4|1|AIML|A': {
                      MON: ['CC Lab', 'DL', 'DL', 'NIC', 'MC', 'DM'],
                      TUE: ['Project Stage-1 Lab', 'PPLE', 'DL', 'NIC', 'MC', 'MC'],
                      WED: ['Project Stage-1 Lab', 'DM', 'PPLE', 'DL', 'NIC', 'NIC'],
                      THU: ['Project Stage-1 Lab', 'MC', 'DM', 'PPLE', 'MENTORING', 'PPLE'],
                      FRI: ['DL', 'NIC', 'MC', 'DM', 'SPORTS', 'PPLE'],
                      SAT: ['DL', 'NIC', 'MC', 'DM', 'PPLE', 'LIBRARY']
                  },
                  'R22|4|1|AIML|B': {
                      MON: ['DL', 'NIC', 'MC', 'CC Lab', 'DM', 'DM'],
                      TUE: ['PPLE', 'DL', 'NIC', 'Project Stage-1 Lab', 'MC', 'MC'],
                      WED: ['DM', 'PPLE', 'DL', 'Project Stage-1 Lab', 'NIC', 'NIC'],
                      THU: ['MC', 'DM', 'PPLE', 'Project Stage-1 Lab', 'MENTORING', 'PPLE'],
                      FRI: ['DL', 'NIC', 'MC', 'DM', 'SPORTS', 'PPLE'],
                      SAT: ['DL', 'NIC', 'MC', 'DM', 'PPLE', 'LIBRARY']
                  },
                 'R22|4|1|IT|': {
                     MON: ['IS Lab', 'IS', 'IS', 'Project Stage-1 Lab', 'SL', 'SL'],
                     TUE: ['CC Lab', 'OE', 'IS', 'CC', 'FSD', 'FSD'],
                     WED: ['FSD Lab', 'SL', 'OE', 'IS', 'CC', 'CC'],
                     THU: ['FSD', 'SL', 'OE', 'IS', 'CC', 'MENTORING'],
                      FRI: ['FSD', 'SL', 'OE', 'IS', 'SPORTS', 'CC'],
                      SAT: ['IS', 'CC', 'FSD', 'SL', 'OE', 'LIBRARY']
                 }
             };
            return plans[key] || null;
        }

        function applyRequiredFixedLayoutsToVisibleTables() {
            return 0;
        }

        function applyR22ThreeOneITDisplayPlan(context) {
            if (!isR22ThreeOneITContext(context)) {
                return false;
            }

            return applyFixedDisplayPlan(context, getRequiredFixedPlanForSpec('R22', '3', '1', 'IT', ''));
        }

        function applyR25TwoOneITDisplayPlan(context) {
            if (!isR25TwoOneITContext(context)) {
                return false;
            }

            return applyFixedDisplayPlan(context, getRequiredFixedPlanForSpec('R25', '2', '1', 'IT', ''));
        }

        function applyR25TwoOneAIMLDisplayPlan(context) {
            if (!isR25TwoOneAIMLContext(context)) {
                return false;
            }

            return applyFixedDisplayPlan(
                context,
                getRequiredFixedPlanForSpec('R25', '2', '1', 'AIML', context.section || 'A')
            );
        }

        function applyR22ThreeOneAIMLDisplayPlan(context) {
            if (!isR22ThreeOneAIMLContext(context)) {
                return false;
            }

            return applyFixedDisplayPlan(
                context,
                getRequiredFixedPlanForSpec('R22', '3', '1', 'AIML', context.section || 'A')
            );
        }

        function applyR22FourOneITDisplayPlan(context) {
            if (!isR22FourOneITContext(context)) {
                return false;
            }

            return applyFixedDisplayPlan(context, getRequiredFixedPlanForSpec('R22', '4', '1', 'IT', ''));
        }

        function applyR22FourOneAIMLDisplayPlan(context) {
            if (!isR22FourOneAIMLContext(context)) {
                return false;
            }

            return applyFixedDisplayPlan(
                context,
                getRequiredFixedPlanForSpec('R22', '4', '1', 'AIML', context.section || 'A')
            );
        }

        function hasVisibleBlankClassSlot(context) {
            return (context && context.slots ? context.slots : []).some(function (slot) {
                const cell = getTimeTableSlotCell(slot);
                return cell && cell.style.display !== 'none' && !slot.value.trim();
            });
        }

        function countClassHoursForLabel(context, label) {
            const normalizedLabel = normalizeSubjectNameForSchedule(label);
            return (context && context.slots ? context.slots : []).reduce(function (total, slot) {
                const cell = getTimeTableSlotCell(slot);
                if (!cell || cell.style.display === 'none' || normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) !== normalizedLabel) {
                    return total;
                }
                return total + (cell.colSpan && cell.colSpan > 1 ? cell.colSpan : 1);
            }, 0);
        }

        function getR22ThreeOneITClassHourSummary(context) {
            const summary = {
                theory: 0,
                lab: 0,
                activity: 0,
                total: 0
            };
            const activities = new Set(['SPORTS', 'LIBRARY', 'MENTORING', 'EVS/IKS', 'VEGS']);
            (context && context.slots ? context.slots : []).forEach(function (slot) {
                const cell = getTimeTableSlotCell(slot);
                if (!cell || cell.style.display === 'none' || !slot.value.trim()) {
                    return;
                }
                const hours = cell.colSpan && cell.colSpan > 1 ? cell.colSpan : 1;
                const value = normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value));
                summary.total += hours;
                if (activities.has(value)) {
                    summary.activity += hours;
                } else if (isLaboratoryScheduleValue(slot.value)) {
                    summary.lab += hours;
                } else {
                    summary.theory += hours;
                }
            });
            return summary;
        }

        function hasR22ThreeOneITActivitiesInLastHours(context) {
            const slots = context && context.slots ? context.slots : [];
            const lastPeriod = periodOrder[periodOrder.length - 1];
            const sportsSlot = getClassSlot('FRI', lastPeriod, slots);
            const librarySlot = getClassSlot('SAT', lastPeriod, slots);
            const mentoringSlot = getClassSlot('THU', lastPeriod, slots);
            return Boolean(sportsSlot) && normalizeSubjectNameForSchedule(getComparableSubjectValue(sportsSlot.value)) === 'SPORTS' &&
                Boolean(librarySlot) && normalizeSubjectNameForSchedule(getComparableSubjectValue(librarySlot.value)) === 'LIBRARY' &&
                Boolean(mentoringSlot) && normalizeSubjectNameForSchedule(getComparableSubjectValue(mentoringSlot.value)) === 'MENTORING';
        }

        function hasCompleteR22ThreeOneITLoad(context) {
            const summary = getR22ThreeOneITClassHourSummary(context);
            const requiredTheoryLabels = ['DAA', 'ACD', 'ES', 'DM', 'DDB'];
            const requiredLabLabels = ['CD Lab', 'Data Mining Lab', 'ES Lab', 'Flutter Lab'];
            return summary.theory === 25 &&
                summary.lab === 8 &&
                summary.activity === 3 &&
                summary.total === 36 &&
                !hasVisibleBlankClassSlot(context) &&
                requiredTheoryLabels.every(function (label) {
                    return countClassHoursForLabel(context, label) > 0;
                }) &&
                requiredLabLabels.every(function (label) {
                    return countClassHoursForLabel(context, label) === 2;
                }) &&
                countClassHoursForLabel(context, 'SPORTS') === 1 &&
                countClassHoursForLabel(context, 'LIBRARY') === 1 &&
                countClassHoursForLabel(context, 'MENTORING') === 1 &&
                hasR22ThreeOneITActivitiesInLastHours(context);
        }

        function isTwoOneITContext(context) {
            return Boolean(context) &&
                normalizeAcademicLevelValue(context.year) === '2' &&
                normalizeAcademicLevelValue(context.semester) === '1' &&
                normalizeClassValue(context.branch) === 'IT';
        }

        function classSlotHasLabel(context, day, period, label) {
            const slot = getClassSlot(day, period, context && context.slots);
            return Boolean(slot) && normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) === normalizeSubjectNameForSchedule(label);
        }

        function hasR25TwoOneITLabPlacement(context, placements) {
            return Object.keys(placements).every(function (label) {
                const placement = placements[label];
                return classSlotHasLabel(context, placement.day, placement.period, label);
            });
        }

        function hasCurrentR25TwoOneITLabPlacement(context) {
            return hasR25TwoOneITLabPlacement(context, {
                'CM Lab': { day: 'MON', period: '9:30-10:30' },
                'Java Lab': { day: 'TUE', period: '9:30-10:30' },
                'OS Lab': { day: 'WED', period: '9:30-10:30' },
                'IoT Lab': { day: 'THU', period: '9:30-10:30' },
                'DV Lab': { day: 'FRI', period: '9:30-10:30' }
            });
        }

        function hasLegacyR25TwoOneITLabPlacement(context) {
            return hasR25TwoOneITLabPlacement(context, {
                'DV Lab': { day: 'MON', period: '9:30-10:30' },
                'OS Lab': { day: 'TUE', period: '9:30-10:30' },
                'Java Lab': { day: 'WED', period: '9:30-10:30' },
                'IoT Lab': { day: 'THU', period: '1:20-2:15' }
            });
        }

        function migrateLegacyR25TwoOneITLabHours(context) {
            if (!isTwoOneITContext(context) || !hasLegacyR25TwoOneITLabPlacement(context)) {
                return false;
            }
            return applyR25TwoOneITDisplayPlan(context);
        }

        function hasCompleteR25TwoOneITLoad(context) {
            const summary = getR22ThreeOneITClassHourSummary(context);
            const requiredTheoryLabels = ['MSF', 'COA', 'OOPJ', 'OS', 'IoT'];
            const requiredLabLabels = ['CM Lab', 'Java Lab', 'OS Lab', 'IoT Lab', 'DV Lab'];
            return summary.theory === 20 &&
                summary.lab === 10 &&
                summary.activity === 6 &&
                summary.total === 36 &&
                !hasVisibleBlankClassSlot(context) &&
                requiredTheoryLabels.every(function (label) {
                    return countClassHoursForLabel(context, label) === 4;
                }) &&
                requiredLabLabels.every(function (label) {
                    return countClassHoursForLabel(context, label) === 2;
                }) &&
                countClassHoursForLabel(context, 'EVS/IKS') === 2 &&
                countClassHoursForLabel(context, 'SPORTS') === 2 &&
                countClassHoursForLabel(context, 'LIBRARY') === 1 &&
                countClassHoursForLabel(context, 'MENTORING') === 1 &&
                hasMergedSportsLastHours(context) &&
                hasCurrentR25TwoOneITLabPlacement(context);
        }

        function hasMergedSportsLastHours(context) {
            const sportsSlot = getClassSlot('FRI', '2:15-3:10', context && context.slots);
            const sportsCell = getTimeTableSlotCell(sportsSlot);
            return Boolean(sportsSlot) &&
                normalizeSubjectNameForSchedule(getComparableSubjectValue(sportsSlot.value)) === 'SPORTS' &&
                sportsCell &&
                sportsCell.colSpan === 2;
        }

        function hasCurrentR25TwoOneAIMLLabPlacement(context) {
            return hasR25TwoOneITLabPlacement(context, {
                'CM Lab': { day: 'MON', period: '9:30-10:30' },
                'Java Lab': { day: 'TUE', period: '9:30-10:30' },
                'SE Lab': { day: 'WED', period: '9:30-10:30' },
                'DBMS Lab': { day: 'THU', period: '9:30-10:30' },
                'NODE JS Lab': { day: 'FRI', period: '9:30-10:30' }
            });
        }

        function hasCompleteR25TwoOneAIMLLoad(context) {
            const summary = getR22ThreeOneITClassHourSummary(context);
            const requiredTheoryLabels = ['MSF', 'COA', 'OOPJ', 'SE', 'DBMS'];
            const requiredLabLabels = ['CM Lab', 'Java Lab', 'SE Lab', 'DBMS Lab', 'NODE JS Lab'];
            return summary.theory === 20 &&
                summary.lab === 10 &&
                summary.activity === 6 &&
                summary.total === 36 &&
                !hasVisibleBlankClassSlot(context) &&
                requiredTheoryLabels.every(function (label) {
                    return countClassHoursForLabel(context, label) === 4;
                }) &&
                requiredLabLabels.every(function (label) {
                    return countClassHoursForLabel(context, label) === 2;
                }) &&
                (countClassHoursForLabel(context, 'VEGS') === 2 || countClassHoursForLabel(context, 'VALUE ETHICS AND GENDER SENSITIZATION') === 2) &&
                countClassHoursForLabel(context, 'SPORTS') === 2 &&
                countClassHoursForLabel(context, 'LIBRARY') === 1 &&
                countClassHoursForLabel(context, 'MENTORING') === 1 &&
                hasMergedSportsLastHours(context) &&
                hasCurrentR25TwoOneAIMLLabPlacement(context);
        }

        function ensureR25TwoOneAIMLCompletePlans() {
            return 0;
        }

        function contextHasRequiredLabels(context, labels) {
            return (labels || []).every(function (label) {
                return countClassHoursForLabel(context, label) > 0;
            });
        }

        function shouldApplyFixedLayout(context, labels) {
            return hasVisibleBlankClassSlot(context) ||
                countClassContextHours(context) !== 36 ||
                !contextHasRequiredLabels(context, labels);
        }

        function isFixedRequiredLayoutContext(context) {
            return isR25TwoOneITContext(context) ||
                isR25TwoOneAIMLContext(context) ||
                isR22ThreeOneITContext(context) ||
                isR22ThreeOneAIMLContext(context) ||
                isR22FourOneITContext(context) ||
                isR22FourOneAIMLContext(context);
        }

        function ensureFixedRequiredLayouts(classContexts) {
            return 0;
        }

        function ensureR22ThreeOneITCompletePlan() {
            return false;
        }

        function ensureR25TwoOneITCompletePlan() {
            return false;
        }

        function refreshIndividualTimeTablesFromCurrentSelections() {
            const selections = getStoredSubjectSelections();
            const contexts = getClassTimeTableContexts(selections);
            const timetableSelections = getSelectionsForClassContexts(selections, contexts);
            return renderIndividualFacultyTimeTables(timetableSelections, contexts);
        }

        function syncIndividualTimeTablesWithMainTables(selections, classContexts) {
            const normalizedSelections = normalizeSubjectSelections(selections || getStoredSubjectSelections());
            const contexts = classContexts || getClassTimeTableContexts(normalizedSelections);
            const timetableSelections = getSelectionsForClassContexts(normalizedSelections, contexts);
            const filledHours = renderIndividualFacultyTimeTables(timetableSelections, contexts);
            normalizeAllTimeTableSlotValues();
            updateLabTimeTable(normalizedSelections, contexts);
            return filledHours;
        }

        function syncClassTimeTablesFromIndividualCard(card, selections, classContexts) {
            if (!card) {
                return false;
            }
            const normalizedSelections = normalizeSubjectSelections(selections || getStoredSubjectSelections());
            const contexts = classContexts || getClassTimeTableContexts(normalizedSelections);
            const facultyName = (getIndividualTimeTableMetaFields(card).find(function (field) {
                return field.getAttribute('aria-label') === 'Faculty Name';
            })?.value || '').trim();
            const employeeCode = (getIndividualTimeTableMetaFields(card).find(function (field) {
                return field.getAttribute('aria-label') === 'Employee Code';
            })?.value || '').trim();
            const schedule = buildIndividualFacultySchedules(normalizedSelections).find(function (item) {
                return (employeeCode && normalizeClassValue(item.employeeCode) === normalizeClassValue(employeeCode)) ||
                    (facultyName && normalizeFacultyNameForSort(item.facultyName) === normalizeFacultyNameForSort(facultyName));
            });
            if (!schedule) {
                return false;
            }
            const scheduleKeys = new Set(schedule.selections.map(getSubjectSelectionDuplicateKey));
            const originalClassValues = new Map();
            contexts.forEach(function (context) {
                context.slots.forEach(function (slot) {
                    originalClassValues.set(slot.dataset.day + '|' + slot.dataset.period, slot.value);
                });
            });
            const slotValues = new Map(getIndividualTimeTableSlots(card).map(function (slot) {
                const rawValue = String(slot.value || '').trim();
                const prefix = contextLabelPrefix(rawValue, contexts);
                return [slot.dataset.day + '|' + slot.dataset.period, {
                    value: rawValue,
                    subject: prefix ? rawValue.slice(prefix.length).trim() : rawValue
                }];
            }));
            let changed = false;
            contexts.forEach(function (context) {
                const labels = getIndividualScheduleLabelsForContext(schedule, context);
                if (!labels.size) {
                    return;
                }
                context.slots.forEach(function (classSlot) {
                    const edited = slotValues.get(classSlot.dataset.day + '|' + classSlot.dataset.period);
                    const original = originalClassValues.get(classSlot.dataset.day + '|' + classSlot.dataset.period);
                    const subject = original ? getComparableSubjectValue(original) : '';
                    if (!subject || !labels.has(normalizeSubjectNameForSchedule(subject)) || !edited) {
                        return;
                    }
                    const assignmentExists = getSelectionsForClassContext(normalizedSelections, context).some(function (selection) {
                        return scheduleKeys.has(getSubjectSelectionDuplicateKey(selection)) &&
                            getScheduleLabelsForSelection(selection).some(function (label) {
                                return normalizeSubjectNameForSchedule(label) === normalizeSubjectNameForSchedule(subject);
                            });
                    });
                    if (!assignmentExists) return;
                    const sameSubject = labels.has(normalizeSubjectNameForSchedule(edited.subject));
                    const nextValue = edited.value && sameSubject
                        ? normalizeTimeTableDisplayValue(edited.subject + (extractLabRoomNumber(classSlot.value) ? ' (LAB ROOM: ' + extractLabRoomNumber(classSlot.value) + ')' : ''))
                        : '';
                    if (original !== nextValue) {
                        classSlot.value = nextValue;
                        changed = true;
                    }
                });
            });
            if (changed) {
                contexts.forEach(function (context) { restoreClassLabMergesFromValues(context.slots); });
                normalizeAllTimeTableSlotValues();
                syncIndividualTimeTablesWithMainTables(normalizedSelections, contexts);
                saveTimeTableData();
            }
            return changed;
        }

        function contextLabelPrefix(value, contexts) {
            const text = String(value || '');
            const match = text.match(/^(.*?)\s+-\s+/);
            if (!match) return '';
            return (contexts || []).some(function (context) {
                return normalizeClassValue(context.label) === normalizeClassValue(match[1]);
            }) ? match[0] : '';
        }

        function extractLabRoomNumber(slotValue) {
            const match = String(slotValue || '').match(/\((?:LAB\s*)?ROOM:\s*([^)]+)\)/i);
            return match ? match[1].trim() : '';
        }

        const LAB_TIME_TABLE_DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
        const LAB_TIME_TABLE_COLUMNS = [
            { type: 'slot', period: '9:30-10:30' },
            { type: 'slot', period: '10:30-11:30' },
            { type: 'slot', period: '11:40-12:40' },
            { type: 'break', label: 'Break' },
            { type: 'slot', period: '1:20-2:15' },
            { type: 'slot', period: '2:15-3:10' },
            { type: 'slot', period: '3:15-4:10' }
        ];

        function resetLabTimeTable() {
            const roomsContainer = document.getElementById('labTimeTableRooms');
            if (roomsContainer) {
                roomsContainer.innerHTML = '<p id="labTimeTableEmpty" class="text-center text-muted mb-0">Generate or load a timetable to view lab sessions.</p>';
            }
            const legendBody = document.getElementById('labTimeTableLegendBody');
            if (legendBody) {
                legendBody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Generate or load a timetable to view lab sessions.</td></tr>';
            }
            setStatus(labTimeTableStatus, 'Lab timetable not saved yet', 'muted');
        }

        function renderLabRoomTimeTableCard(roomData) {
            const headerCells = LAB_TIME_TABLE_COLUMNS.map(function (column) {
                return '<th>' + (column.type === 'break' ? 'Break' : escapeHtml(column.period)) + '</th>';
            }).join('');

            const bodyRows = LAB_TIME_TABLE_DAYS.map(function (day) {
                const cells = LAB_TIME_TABLE_COLUMNS.map(function (column) {
                    if (column.type === 'break') {
                        return '<td class="break-slot">Break</td>';
                    }
                    const entries = roomData.cells.get(day + '|' + column.period) || [];
                    if (!entries.length) {
                        return '<td class="lab-slot-cell"></td>';
                    }
                    const content = entries.map(function (entry) {
                        const classText = entry.class
                            ? '<span class="lab-slot-class">' + escapeHtml(entry.class) + '</span>'
                            : '';
                        const facultyText = entry.faculty
                            ? '<span class="lab-slot-faculty">' + escapeHtml(entry.faculty) + '</span>'
                            : '';
                        return '<div class="lab-slot-entry">' +
                            '<span class="lab-slot-subject">' + escapeHtml(entry.subject) + '</span>' +
                            classText +
                            facultyText +
                            '</div>';
                    }).join('');
                    return '<td class="lab-slot-cell lab-occupied">' + content + '</td>';
                }).join('');
                return '<tr><td>' + day + '</td>' + cells + '</tr>';
            }).join('');

            return '<div class="lab-room-timetable">' +
                '<div class="lab-room-timetable-header"><i class="fas fa-door-open"></i>Lab Room ' + escapeHtml(roomData.room) + '</div>' +
                '<div class="table-responsive" style="overflow-x: auto;">' +
                '<table class="table exam-table time-table-grid lab-time-table-grid align-middle mb-0">' +
                '<thead><tr><th>Day</th>' + headerCells + '</tr></thead>' +
                '<tbody>' + bodyRows + '</tbody>' +
                '</table>' +
                '</div>' +
                '</div>';
        }

        function updateLabTimeTable(selections, classContexts) {
            const roomsContainer = document.getElementById('labTimeTableRooms');
            const legendBody = document.getElementById('labTimeTableLegendBody');
            const labEntries = [];
            const legendEntryKeys = new Set();
            const normalizedSelections = normalizeSubjectSelections(selections || getStoredSubjectSelections());
            const contexts = classContexts || getClassTimeTableContexts(normalizedSelections);

            // Group all lab sessions from the main and individual time tables by lab room number.
            const rooms = new Map();

            contexts.forEach(function (context) {
                const contextSelections = getSelectionsForClassContext(normalizedSelections, context);
                const assignments = buildClassAssignments(contextSelections, context);
                (context.slots || []).forEach(function (slot) {
                    const rawValue = (slot.value || '').trim();
                    if (!rawValue) {
                        return;
                    }
                    const day = slot.dataset.day || '';
                    const period = slot.dataset.period || '';
                    if (!day || !period) {
                        return;
                    }
                    const comparableValue = getComparableSubjectValue(rawValue);
                    const assignment = assignments.find(function (candidate) {
                        return normalizeSubjectNameForSchedule(candidate.displayName || candidate.subjectName) ===
                            normalizeSubjectNameForSchedule(comparableValue);
                    });
                    const assignedRoom = assignment && String(assignment.labRoomNumber || '').trim();
                    if (!isLaboratorySubject(rawValue) && !(assignment && assignment.isLab) && !assignedRoom) {
                        return;
                    }
                    const labRoom = extractLabRoomNumber(rawValue) || assignedRoom || getStandardLabRoomNumber(comparableValue) || 'Unassigned';
                    const roomKey = getLabRoomKey(labRoom) || 'UNASSIGNED';
                    const subjectDisplay = getShortSubjectLabel(comparableValue) || comparableValue || rawValue;
                    const faculty = (assignment || {}).facultyKey || '';

                    if (!rooms.has(roomKey)) {
                        rooms.set(roomKey, { room: labRoom, cells: new Map() });
                    }
                    const roomData = rooms.get(roomKey);
                    const periodIndex = periodOrder.indexOf(period);
                    const cell = getTimeTableSlotCell(slot);
                    const duration = cell && cell.colSpan > 1 ? cell.colSpan : 1;
                    for (let offset = 0; offset < duration; offset += 1) {
                        const occupiedPeriod = periodOrder[periodIndex + offset];
                        if (!occupiedPeriod) {
                            continue;
                        }
                        const cellKey = day + '|' + occupiedPeriod;
                        if (!roomData.cells.has(cellKey)) {
                            roomData.cells.set(cellKey, []);
                        }
                        const cellEntries = roomData.cells.get(cellKey);
                        const duplicate = cellEntries.some(function (existing) {
                            return existing.class === (context.label || '') &&
                                normalizeSubjectNameForSchedule(existing.subject) === normalizeSubjectNameForSchedule(subjectDisplay);
                        });
                        if (!duplicate) {
                            cellEntries.push({
                                subject: subjectDisplay,
                                class: context.label || '',
                                faculty: faculty
                            });
                        }
                    }

                    const legendEntryKey = [context.label || '', subjectDisplay, roomKey, faculty].join('|');
                    if (!legendEntryKeys.has(legendEntryKey)) {
                        legendEntryKeys.add(legendEntryKey);
                        labEntries.push({
                            day: day,
                            period: period,
                            subject: subjectDisplay,
                            labRoom: labRoom,
                            class: context.label || '',
                            faculty: faculty
                        });
                    }
                });
            });

            if (roomsContainer) {
                if (rooms.size) {
                    const sortedRooms = Array.from(rooms.values()).sort(function (a, b) {
                        return String(a.room).localeCompare(String(b.room), undefined, { numeric: true, sensitivity: 'base' });
                    });
                    roomsContainer.innerHTML = sortedRooms.map(renderLabRoomTimeTableCard).join('');
                } else {
                    roomsContainer.innerHTML = '<p id="labTimeTableEmpty" class="text-center text-muted mb-0">No lab sessions found.</p>';
                }
            }

            if (legendBody) {
                if (labEntries.length) {
                    legendBody.innerHTML = labEntries.map(function (entry) {
                        return '<tr>' +
                            '<td>' + escapeHtml(entry.class) + '</td>' +
                            '<td>' + escapeHtml(entry.subject) + '</td>' +
                            '<td>' + escapeHtml(entry.labRoom) + '</td>' +
                            '<td>' + escapeHtml(entry.faculty) + '</td>' +
                            '</tr>';
                    }).join('');
                } else {
                    legendBody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No lab sessions found.</td></tr>';
                }
            }

            if (labEntries.length) {
                const sessionLabel = labEntries.length === 1 ? 'lab session' : 'lab sessions';
                setStatus(labTimeTableStatus, 'Showing ' + labEntries.length + ' ' + sessionLabel + ' from the saved timetable', 'success');
            } else {
                setStatus(labTimeTableStatus, 'No lab sessions in the current timetable', 'warning');
            }

            return labEntries.length;
        }

        function getTimeTableClassSelections(selections) {
            const branch = normalizeClassValue(timeTableBranchField ? timeTableBranchField.value : 'IT');
            const year = normalizeClassValue(timeTableYearField ? timeTableYearField.value : '3');
            const semester = normalizeClassValue(timeTableSemesterField ? timeTableSemesterField.value : '1');
            const regulation = normalizeClassValue(subjectSelectionFields.regulation ? subjectSelectionFields.regulation.value : 'R22');

            return normalizeSubjectSelections(selections || getStoredSubjectSelections()).filter(function (selection) {
                return normalizeClassValue(selection.branch) === branch &&
                    normalizeClassValue(selection.regulation || 'R22') === regulation &&
                    normalizeClassValue(selection.year) === year &&
                    normalizeClassValue(selection.semester) === semester &&
                    ((selection.subjectCode || '').trim() || (selection.subjectName || '').trim());
            });
        }

        function filterSubjectsByFacultySelections(subjects, selections) {
            const availableSelections = getTimeTableClassSelections(selections);
            const selectedCodes = availableSelections.map(function (selection) {
                return normalizeClassValue(selection.subjectCode);
            }).filter(Boolean);
            const selectedNames = availableSelections.map(function (selection) {
                return normalizeClassValue(selection.subjectName);
            }).filter(Boolean);

            if (!selectedCodes.length && !selectedNames.length) {
                return [];
            }

            return (Array.isArray(subjects) ? subjects : []).filter(function (subject) {
                const code = normalizeClassValue(subject.code);
                const name = normalizeClassValue(subject.name);
                return selectedCodes.includes(code) || selectedNames.includes(name);
            });
        }

        function pruneUnselectedTimeTableSubjects(subjects, selections) {
            const availableSelections = getTimeTableClassSelections(selections);
            const selectedValues = new Set();
            availableSelections.forEach(function (selection) {
                selectedValues.add(normalizeClassValue(selection.subjectCode));
                selectedValues.add(normalizeClassValue(selection.subjectName));
            });

            const syllabusValues = new Set();
            (Array.isArray(subjects) ? subjects : []).forEach(function (subject) {
                syllabusValues.add(normalizeClassValue(subject.code));
                syllabusValues.add(normalizeClassValue(subject.name));
            });

            if (!syllabusValues.size) {
                return;
            }

            let changed = false;
            timeTableSlots.concat(getIndividualTimeTableSlots()).forEach(function (slot) {
                const currentValue = normalizeClassValue(slot.value);
                if (currentValue && syllabusValues.has(currentValue) && !selectedValues.has(currentValue)) {
                    slot.value = '';
                    changed = true;
                }
            });

            if (changed) {
                markTimeTableDirty();
            }
        }

        function loadSubjectSelectionSubjects(selectedSubject) {
            if (!syllabusSubjectsUrl || !subjectSelectionFields.year || !subjectSelectionFields.semester || !subjectSelectionFields.branch || !subjectSelectionFields.regulation) {
                return;
            }

            const params = new URLSearchParams({
                regulation: subjectSelectionFields.regulation.value || 'R22',
                year: subjectSelectionFields.year.value || '3',
                semester: subjectSelectionFields.semester.value || '1',
                branch: subjectSelectionFields.branch.value || 'IT',
                section: subjectSelectionFields.section ? (subjectSelectionFields.section.value || 'A') : 'A'
            });

            fetch(syllabusSubjectsUrl + '?' + params.toString(), {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error('Could not load subject selection subjects.');
                    }
                    return response.json();
                })
                .then(function (data) {
                    syncSubjectSelectionOptions(data);
                    renderSubjectSelectionSubjects(Array.isArray(data.subjects) ? data.subjects : [], selectedSubject);
                })
                .catch(function (error) {
                    console.error(error);
                    renderSubjectSelectionSubjects([], '');
                    setStatus(subjectSelectionStatus, 'Could not load subjects for the selected class', 'warning');
                });
        }

        function loadSyllabusSubjects(selectedCode) {
            if (!syllabusSubjectsUrl || !timeTableYearField || !timeTableSemesterField || !timeTableBranchField) {
                return Promise.resolve();
            }

            const romanMap = { I: '1', II: '2', III: '3', IV: '4' };
            if (romanMap[timeTableYearField.value]) {
                timeTableYearField.value = romanMap[timeTableYearField.value];
            }
            if (romanMap[timeTableSemesterField.value]) {
                timeTableSemesterField.value = romanMap[timeTableSemesterField.value];
            }
            if (!timeTableYearField.value) {
                timeTableYearField.value = '3';
            }
            if (!timeTableSemesterField.value) {
                timeTableSemesterField.value = '1';
            }
            if (!timeTableBranchField.value) {
                timeTableBranchField.value = 'IT';
            }

            const params = new URLSearchParams({
                year: timeTableYearField.value || '3',
                semester: timeTableSemesterField.value || '1',
                branch: timeTableBranchField.value || 'IT'
            });

            return fetch(syllabusSubjectsUrl + '?' + params.toString(), {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error('Could not load syllabus subjects.');
                    }
                    return response.json();
                })
                .then(function (data) {
                    const allSubjects = Array.isArray(data.subjects) ? data.subjects : [];
                    const filteredSubjects = filterSubjectsByFacultySelections(allSubjects);
                    renderSyllabusSubjects(filteredSubjects, selectedCode);
                    renderCourseReference();
                    pruneUnselectedTimeTableSubjects(allSubjects);
                    data.subjects = filteredSubjects;
                    return data;
                })
                .catch(function (error) {
                    console.error(error);
                    renderSyllabusSubjects([], '');
                    renderCourseReference();
                    setStatus(timeTableStatus, 'Could not load subjects from syllabus', 'warning');
                    return { subjects: [] };
                });
        }

        function useSubjectInLessonPlan(subject) {
            if (!subject) {
                return;
            }
            if (lessonHeaderFields.subject) {
                lessonHeaderFields.subject.value = subject.name || '';
            }
            if (lessonHeaderFields.subjectCode) {
                lessonHeaderFields.subjectCode.value = subject.code || '';
            }
            markLessonDirty();
        }

        function submitLessonPlanDownload(payload) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = lessonPlanDownloadUrl;
            form.style.display = 'none';

            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = getCsrfToken();

            const payloadInput = document.createElement('input');
            payloadInput.type = 'hidden';
            payloadInput.name = 'lesson_plan_payload';
            payloadInput.value = JSON.stringify(payload);

            form.appendChild(csrfInput);
            form.appendChild(payloadInput);
            document.body.appendChild(form);
            form.submit();
            form.remove();
        }

        function markLessonDirty() {
            setStatus(lessonPlanStatus, 'Lesson plan has unsaved changes', 'warning');
        }

        function markEvaluationDirty() {
            setStatus(evaluationSaveStatus, 'Evaluation has unsaved changes', 'warning');
        }

        function markTimeTableDirty() {
            renderAllTimeTableLoadSummaries();
            setStatus(timeTableStatus, 'Timetable has unsaved changes', 'warning');
        }

        function setTimetableFieldsEditable(root, enabled) {
            if (!root) return;
            root.querySelectorAll('.timetable-slot, .empty-timetable-slot, .individual-timetable-slot').forEach(function (field) {
                field.readOnly = !enabled;
                field.classList.toggle('timetable-readonly', !enabled);
            });
        }

        function initializeTimetableEditState() {
            setTimetableFieldsEditable(document.getElementById('timeTableGrid'), false);
            emptyTimeTableCards.forEach(function (card) { setTimetableFieldsEditable(card, false); });
            getIndividualTimeTableCards().forEach(function (card) { setTimetableFieldsEditable(card, false); });
        }

        function markSubjectSelectionDirty() {
            setStatus(subjectSelectionStatus, 'Subject selection has unsaved changes', 'warning');
        }

        function getDayName(date) {
            const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            return days[new Date(date).getDay()] || '';
        }

        function formatDate(date) {
            const instance = new Date(date);
            const day = String(instance.getDate()).padStart(2, '0');
            const month = String(instance.getMonth() + 1).padStart(2, '0');
            const year = instance.getFullYear();
            return day + '-' + month + '-' + year;
        }

        function createDefaultRow() {
            return {
                date: '',
                day: '',
                weekNum: 1,
                classesTaken: '',
                topics: '',
                studentsPresent: ''
            };
        }

        function clearLessonRows() {
            lessonPlanBody.innerHTML = '';
        }

        function updateLessonTotals() {
            let runningTotal = 0;
            lessonPlanBody.querySelectorAll('.classes-taken-input').forEach(function (input) {
                const value = Number(input.value || 0);
                if (!Number.isNaN(value)) {
                    runningTotal += value;
                }
            });
            document.getElementById('totalClassesTaken').value = runningTotal;
        }

        function renderLessonRows(rows) {
            clearLessonRows();
            const safeRows = rows && rows.length ? rows : [createDefaultRow()];

            const grouped = [];
            safeRows.forEach(function (entry) {
                const weekKey = Number(entry.weekNum || 1);
                const lastGroup = grouped[grouped.length - 1];
                if (lastGroup && lastGroup.weekNum === weekKey) {
                    lastGroup.rows.push(entry);
                } else {
                    grouped.push({ weekNum: weekKey, rows: [entry] });
                }
            });

            let serialNumber = 1;
            grouped.forEach(function (group) {
                group.rows.forEach(function (entry, index) {
                    const row = document.createElement('tr');
                    row.dataset.weekNum = String(group.weekNum);

                    const serialCell = document.createElement('td');
                    serialCell.innerHTML = '<input type="text" class="form-control text-center lesson-serial-input" value="' + serialNumber + '" readonly />';

                    const dateCell = document.createElement('td');
                    dateCell.innerHTML = '<input type="text" class="form-control lesson-date-input" value="' + (entry.date || '') + '" readonly />';

                    const dayCell = document.createElement('td');
                    dayCell.innerHTML = '<input type="text" class="form-control lesson-day-input" value="' + (entry.day || '') + '" readonly />';

                    const classesCell = document.createElement('td');
                    classesCell.innerHTML = '<input type="number" class="form-control classes-taken-input" value="' + (entry.classesTaken || '') + '" min="0" step="1" />';

                    const topicsCell = document.createElement('td');
                    topicsCell.innerHTML = '<textarea class="form-control topics-input" rows="2">' + (entry.topics || '') + '</textarea>';

                    const studentsCell = document.createElement('td');
                    studentsCell.innerHTML = '<input type="number" class="form-control students-input" value="' + (entry.studentsPresent || '') + '" min="0" step="1" />';

                    row.appendChild(serialCell);
                    row.appendChild(dateCell);
                    row.appendChild(dayCell);

                    if (index === 0) {
                        const weekCell = document.createElement('td');
                        weekCell.rowSpan = group.rows.length || 1;
                        weekCell.style.cssText = 'vertical-align: middle; text-align: center;';
                        weekCell.innerHTML = '<input type="text" class="form-control text-center" value="' + group.weekNum + '" readonly />';
                        row.appendChild(weekCell);
                    }

                    row.appendChild(classesCell);
                    row.appendChild(topicsCell);
                    row.appendChild(studentsCell);
                    lessonPlanBody.appendChild(row);
                    serialNumber += 1;
                });
            });

            updateLessonTotals();
        }

        function getLessonHeaderData() {
            return {
                branch: lessonHeaderFields.branch.value,
                year: lessonHeaderFields.year.value,
                semester: lessonHeaderFields.semester.value,
                faculty: lessonHeaderFields.faculty.value,
                employeeCode: lessonHeaderFields.employeeCode.value,
                subject: lessonHeaderFields.subject.value,
                className: lessonHeaderFields.className.value,
                subjectCode: lessonHeaderFields.subjectCode.value
            };
        }

        function setLessonHeaderData(data) {
            const payload = data || {};
            lessonHeaderFields.branch.value = payload.branch || '';
            lessonHeaderFields.year.value = payload.year || '';
            lessonHeaderFields.semester.value = payload.semester || '';
            lessonHeaderFields.faculty.value = payload.faculty || '';
            lessonHeaderFields.employeeCode.value = payload.employeeCode || '';
            lessonHeaderFields.subject.value = payload.subject || '';
            lessonHeaderFields.className.value = payload.className || '';
            lessonHeaderFields.subjectCode.value = payload.subjectCode || '';
        }

        function getLessonTableRows() {
            return Array.from(lessonPlanBody.querySelectorAll('tr')).map(function (row) {
                return {
                    date: row.querySelector('.lesson-date-input') ? row.querySelector('.lesson-date-input').value : '',
                    day: row.querySelector('.lesson-day-input') ? row.querySelector('.lesson-day-input').value : '',
                    weekNum: Number(row.dataset.weekNum || 1),
                    classesTaken: row.querySelector('.classes-taken-input') ? row.querySelector('.classes-taken-input').value : '',
                    topics: row.querySelector('.topics-input') ? row.querySelector('.topics-input').value : '',
                    studentsPresent: row.querySelector('.students-input') ? row.querySelector('.students-input').value : ''
                };
            });
        }

        function saveTeachingPlan() {
            const payload = {
                header: getLessonHeaderData(),
                rows: getLessonTableRows(),
                totalClassesTaken: document.getElementById('totalClassesTaken').value || '0',
                savedAt: new Date().toISOString()
            };

            const hasContent = payload.rows.some(function (row) {
                return row.date || row.day || row.topics || row.classesTaken || row.studentsPresent;
            });

            if (!hasContent) {
                setStatus(lessonPlanStatus, 'Add at least one lesson row before downloading Excel', 'warning');
                return;
            }

            localStorage.setItem(lessonStorageKey, JSON.stringify(payload));
            setStatus(
                lessonPlanStatus,
                'Lesson plan saved. Excel download is starting for ' + formatSavedTime(payload.savedAt),
                'success'
            );
            submitLessonPlanDownload(payload);
        }

        function loadTeachingPlan() {
            const saved = localStorage.getItem(lessonStorageKey);
            if (!saved) {
                renderLessonRows([createDefaultRow()]);
                setStatus(lessonPlanStatus, 'Lesson plan not saved yet', 'muted');
                return;
            }

            try {
                const payload = JSON.parse(saved);
                setLessonHeaderData(payload.header || {});
                renderLessonRows(Array.isArray(payload.rows) && payload.rows.length ? payload.rows : [createDefaultRow()]);
                setStatus(lessonPlanStatus, 'Lesson plan loaded from ' + formatSavedTime(payload.savedAt), 'success');
            } catch (error) {
                console.error('Failed to load saved lesson plan', error);
                renderLessonRows([createDefaultRow()]);
                setStatus(lessonPlanStatus, 'Could not read saved lesson plan', 'warning');
            }
        }

        function addRowsFromRange() {
            const fromDateStr = document.getElementById('fromDate').value;
            const toDateStr = document.getElementById('toDate').value;

            if (!fromDateStr || !toDateStr) {
                alert('Please select both From and To dates.');
                return;
            }

            const fromDate = new Date(fromDateStr);
            const toDate = new Date(toDateStr);

            if (fromDate > toDate) {
                alert('From date must be before To date.');
                return;
            }

            if (getLessonTableRows().some(function (row) {
                return row.date || row.topics || row.classesTaken || row.studentsPresent;
            })) {
                if (!confirm('This will replace the current lesson rows. Continue?')) {
                    return;
                }
            }

            const dates = [];
            let currentDate = new Date(fromDate);
            while (currentDate <= toDate) {
                dates.push(new Date(currentDate));
                currentDate.setDate(currentDate.getDate() + 1);
            }

            let weekNum = 1;
            const rows = dates.map(function (date, index) {
                if (index > 0 && date.getDay() === 1) {
                    weekNum += 1;
                }
                return {
                    date: formatDate(date),
                    day: getDayName(date),
                    weekNum: weekNum,
                    classesTaken: '',
                    topics: '',
                    studentsPresent: ''
                };
            });

            renderLessonRows(rows);
            document.getElementById('fromDate').value = '';
            document.getElementById('toDate').value = '';
            markLessonDirty();
        }

        function deleteTeachingPlan() {
            if (!confirm('Delete the saved lesson plan and clear all rows?')) {
                return;
            }
            localStorage.removeItem(lessonStorageKey);
            setLessonHeaderData({});
            renderLessonRows([createDefaultRow()]);
            setStatus(lessonPlanStatus, 'Lesson plan cleared', 'muted');
        }

        const allDefaultEvaluationRollNumbers = [
            '23C11A1208', '23C11A1224',
            '24C11A1201', '24C11A1202', '24C11A1203', '24C11A1204', '24C11A1205',
            '24C11A1206', '24C11A1207', '24C11A1208', '24C11A1209', '24C11A1210',
            '24C11A1211', '24C11A1212', '24C11A1213', '24C11A1214', '24C11A1215',
            '24C11A1217', '24C11A1218', '24C11A1219', '24C11A1221', '24C11A1223',
            '24C11A1225', '24C11A1226', '24C11A1227', '24C11A1228', '24C11A1229',
            '24C11A1230', '24C11A1231', '24C11A1232', '24C11A1233', '24C11A1234',
            '24C11A1235', '24C11A1236', '24C11A1237', '24C11A1238', '24C11A1239',
            '24C11A1240', '24C11A1241', '24C11A1243', '24C11A1244', '24C11A1245',
            '24C11A1247', '24C11A1248', '24C11A1249', '24C11A1250', '24C11A1251',
            '24C11A1252', '24C11A1254', '24C11A1255', '24C11A1256', '24C11A1257',
            '24C11A1258', '24C11A1259', '24C11A1260', '24C11A1261'
        ];

        const excludedEvaluationOneRollNumbers = new Set([
            '23C11A1208', '24C11A1202', '24C11A1213', '24C11A1218',
            '24C11A1221', '24C11A1228', '24C11A1259'
        ]);
        const defaultEvaluationRollNumbers = allDefaultEvaluationRollNumbers.filter(function (rollNo) {
            return !excludedEvaluationOneRollNumbers.has(rollNo);
        });

        const allDefaultEvaluationAttendance = [
            15.15, 46.97, 56.06, 0.00, 72.73, 75.76, 66.67, 71.21, 80.30, 65.15, 42.42, 48.48, 72.73, 84.85,
            0.00, 75.76, 65.15, 60.61, 21.21, 75.76, 19.70, 68.18, 86.36, 83.33, 84.85, 15.15, 83.33, 87.88,
            62.12, 74.24, 48.48, 69.70, 66.67, 59.09, 37.88, 72.73, 57.58, 37.88, 69.70, 62.12, 84.85, 75.76,
            40.91, 86.36, 33.33, 83.33, 46.97, 72.73, 69.70, 75.76, 37.88, 77.27, 54.55, 27.27, 59.09, 83.33
        ];
        const defaultEvaluationAttendance = allDefaultEvaluationRollNumbers.reduce(function (attendance, rollNo, index) {
            if (!excludedEvaluationOneRollNumbers.has(rollNo)) {
                attendance.push(allDefaultEvaluationAttendance[index]);
            }
            return attendance;
        }, []);
        const secondEvaluationRollNumbers = [
            '24C11A1222',
            '25C11A1202', '25C11A1203', '25C11A1204', '25C11A1205',
            '25C11A1206', '25C11A1207', '25C11A1208', '25C11A1209',
            '25C11A1210', '25C11A1211', '25C11A1212', '25C11A1213',
            '25C11A1214', '25C11A1215', '25C11A1216', '25C11A1217',
            '25C11A1218', '25C11A1219', '25C11A1220', '25C11A1221',
            '25C11A1222', '25C11A1223', '25C11A1224', '25C11A1225',
            '25C11A1226', '25C11A1227', '25C11A1228', '25C11A1229',
            '25C11A1230', '25C11A1231', '25C11A1232', '25C11A1233',
            '25C11A1234', '25C11A1235', '26C15A1201'
        ];
        const secondEvaluationAttendance = [
            6.45, 29.03, 48.39, 58.06, 58.06, 93.55, 45.16, 77.42, 54.84,
            54.84, 67.74, 38.71, 54.84, 77.42, 48.39, 51.61, 29.03, 67.74,
            67.74, 54.84, 64.52, 45.16, 70.97, 77.42, 87.10, 64.52, 83.87,
            74.19, 61.29, 58.06, 58.06, 70.97, 51.61, 64.52, 77.42, 77.78
        ];
        const firstEvaluationObjectiveMarks = [
            'AB', 9, 10, 'AB', 10, 4, 8, 10, 10, 9,
            7, 7, 10, 10, 'AB', 8, 8, 8, 7, 10,
            10, 7, 5, 9, 9, 8, 9, 8, 10, 10,
            8, 6, 7, 9, 9, 9, 8, 8, 8, 'AB',
            10, 5, 8, 10, 10, 10, 10, 7, 10, 9,
            10, 10, 10, 10, 9, 9
        ];
        const firstEvaluationObjectiveMarksVersion = 2;
        const firstEvaluationAssignmentMarks = [
            '', 5, 5, '', 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
            '', 5, 5, 5, 5, 5, '', 5, 5, 5, 5, 5, 5, 5,
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, '', 5,
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5
        ];
        const firstEvaluationAssignmentMarksVersion = 2;
        const firstEvaluationMid2ObjectiveMarks = new Array(56).fill(0);
        const firstEvaluationMid2ObjectiveMarksVersion = 2;
        const firstEvaluationVivaMarks = [
            '', 5, 5, '', 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
            '', 5, 5, 5, 5, 5, '', 5, 5, 5, 5, 5, 5, 5,
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, '', 5,
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5
        ];
        const firstEvaluationVivaMarksVersion = 1;
        const secondEvaluationObjectiveMarks = [
            6, 10, 7, 8, 8, 8, 8, 6, 9, 7,
            9, 9, 6, 8, 8, 8, 7, 8, 8, 9,
            7, 5, 6, 2, 5, 8, 9, 10, 9, 4,
            4, 8, 5, 8, 10, 7
        ];
        const excludedEvaluationThreeRollNumbers = new Set([
            '23C11A1208', '24C11A1202', '24C11A1213', '24C11A1218',
            '24C11A1221', '24C11A1228', '24C11A1259'
        ]);
        const thirdEvaluationRollNumbers = defaultEvaluationRollNumbers.slice();
        const allThirdEvaluationAttendance = [
            17.65, 70.59, 70.59, 0, 88.24, 94.12, 64.71, 88.24, 88.24, 82.35, 47.06, 64.71, 82.35, 82.35,
            0, 76.47, 82.35, 88.24, 23.53, 82.35, 23.53, 64.71, 76.47, 76.47, 76.47, 23.53, 82.35, 82.35,
            88.24, 82.35, 47.06, 82.35, 82.35, 76.47, 70.59, 70.59, 82.35, 35.29, 94.12, 47.06, 82.35, 76.47,
            76.47, 82.35, 47.06, 82.35, 82.35, 94.12, 64.71, 94.12, 52.94, 82.35, 82.35, 29.41, 64.71, 82.35
        ];
        const thirdEvaluationAttendance = allDefaultEvaluationRollNumbers.reduce(function (attendance, rollNo, index) {
            if (!excludedEvaluationThreeRollNumbers.has(rollNo)) {
                attendance.push(allThirdEvaluationAttendance[index]);
            }
            return attendance;
        }, []);
        const fourthEvaluationRollNumbers = [
            '25C11A6601', '25C11A6602', '25C11A6603', '25C11A6604', '25C11A6605',
            '25C11A6606', '25C11A6607', '25C11A6608', '25C11A6609', '25C11A6610',
            '25C11A6611', '25C11A6613', '25C11A6614', '25C11A6615', '25C11A6616',
            '25C11A6617', '25C11A6618', '25C11A6619', '25C11A6620', '25C11A6621',
            '25C11A6622', '25C11A6623', '25C11A6624', '25C11A6625', '25C11A6626',
            '25C11A6627', '25C11A6628', '25C11A6629', '25C11A6630', '25C11A6631',
            '25C11A6632', '25C11A6633', '25C11A6634', '25C11A6635', '25C11A6636',
            '25C11A6637', '25C11A6638', '25C11A6639', '25C11A6640', '25C11A6641',
            '25C11A6642', '25C11A6643', '25C11A6644', '25C11A6646', '25C11A6647',
            '25C11A6648', '25C11A6649', '25C11A6650', '25C11A6651', '25C11A6652',
            '25C11A6654', '25C11A6655', '25C11A6656', '25C11A6657', '25C11A6658',
            '25C11A6659', '25C11A6660', '25C11A6661', '25C11A6662', '25C11A6663',
            '25C11A6664', '25C11A6665'
        ];
        const fourthEvaluationAttendance = [
            83, 72, 83, 94, 83, 94, 94, 83, 78, 78,
            89, 67, 78, 83, 83, 72, 89, 94, 78, 94,
            72, 89, 83, 72, 94, 94, 83, 89, 83, 67,
            100, 78, 94, 56, 83, 83, 61, 83, 94, 83,
            56, 72, 78, 89, 89, 83, 61, 94, 78, 78,
            0, 67, 61, 78, 83, 61, 89, 94, 72, 89,
            89, 78
        ];
        const fourthEvaluationProjectMarks = [
            5, 4, 5, 4, 5, 4, 5, 4, 4, 0,
            5, 4, 5, 5, 4, 5, 4, 5, 5, 4,
            5, 4, 4, 5, 4, 5, 5, 5, 4, 4,
            5, 4, 5, 5, 4, 0, 0, 0, 5, 4,
            4, 0, 4, 4, 5, 5, 4, 5, 4, 4,
            0, 4, 4, 4, 5, 4, 4, 4, 5, 4,
            5, 4
        ];
        const fourthEvaluationProjectMarksVersion = 2;
        const evaluationAttendanceVersion = 9;
        const secondEvaluationObjectiveMarksVersion = 1;

        function getActiveEvaluationStorageKey() {
            return evaluationStorageKeys[activeEvaluationSheet]
                || ('examBranchEvaluationDataSheet' + activeEvaluationSheet);
        }

        function getEvaluationOneRollNumbers() {
            const evaluationOneBody = marksBodyMap['1'];
            if (evaluationOneBody) {
                const currentRollNumbers = Array.from(evaluationOneBody.querySelectorAll('.roll-no'))
                    .map(function (input) { return input.value.trim(); });
                if (currentRollNumbers.length) return currentRollNumbers;
            }
            return defaultEvaluationRollNumbers.slice();
        }

        function getEvaluationOneSeedIndex(student, index) {
            const originalIndex = allDefaultEvaluationRollNumbers.indexOf(String(student.rollNo || '').trim());
            return originalIndex === -1 ? index : originalIndex;
        }

        function getActiveEvaluationRollNumbers() {
            console.log('Active evaluation sheet:', activeEvaluationSheet);
            if (activeEvaluationSheet === '2') {
                return secondEvaluationRollNumbers;
            } else if (activeEvaluationSheet === '3') {
                return thirdEvaluationRollNumbers;
            } else if (activeEvaluationSheet === '4') {
                return fourthEvaluationRollNumbers;
            }
            return activeEvaluationSheet === '1' ? defaultEvaluationRollNumbers : [];
        }

        function getActiveEvaluationAttendance() {
            if (activeEvaluationSheet === '1') return defaultEvaluationAttendance;
            if (activeEvaluationSheet === '2') return secondEvaluationAttendance;
            if (activeEvaluationSheet === '3') return thirdEvaluationAttendance;
            if (activeEvaluationSheet === '4') return fourthEvaluationAttendance;
            return [];
        }

        function generateStudents(count) {
            const students = [];
            const activeRollNumbers = getActiveEvaluationRollNumbers();
            const activeAttendance = getActiveEvaluationAttendance();
            for (let index = 1; index <= count; index += 1) {
                const evaluationOneSeedIndex = activeEvaluationSheet === '1'
                    ? allDefaultEvaluationRollNumbers.indexOf(activeRollNumbers[index - 1])
                    : index - 1;
                const seedMid1Obj = (activeEvaluationSheet === '1'
                    && firstEvaluationObjectiveMarks[evaluationOneSeedIndex] !== undefined)
                    ? String(firstEvaluationObjectiveMarks[evaluationOneSeedIndex])
                    : (activeEvaluationSheet === '2'
                        && secondEvaluationObjectiveMarks[index - 1] !== undefined
                        ? String(secondEvaluationObjectiveMarks[index - 1]) : '');
                const seedAssignment = (activeEvaluationSheet === '1'
                    && firstEvaluationAssignmentMarks[evaluationOneSeedIndex] !== undefined
                    && firstEvaluationAssignmentMarks[evaluationOneSeedIndex] !== '')
                    ? String(firstEvaluationAssignmentMarks[evaluationOneSeedIndex]) : '';
                const seedMid2Obj = activeEvaluationSheet === '1'
                    ? String(firstEvaluationMid2ObjectiveMarks[evaluationOneSeedIndex] || 0)
                    : (activeEvaluationSheet === '2' ? '0' : '');
                const seedViva = (activeEvaluationSheet === '1'
                    && firstEvaluationVivaMarks[evaluationOneSeedIndex] !== undefined
                    && firstEvaluationVivaMarks[evaluationOneSeedIndex] !== '')
                    ? String(firstEvaluationVivaMarks[evaluationOneSeedIndex]) : '';
                if (activeEvaluationSheet === '3' || activeEvaluationSheet === '4') {
                    const seedProject = activeEvaluationSheet === '4'
                        ? (fourthEvaluationProjectMarks[index - 1] !== undefined ? String(fourthEvaluationProjectMarks[index - 1]) : '')
                        : '';
                    students.push({
                        rollNo: activeRollNumbers[index - 1] || '',
                        attendance: index <= activeAttendance.length ? String(activeAttendance[index - 1]) : '',
                        mid1Cia: '',
                        mid1Viva: '',
                        mid1Exam: '',
                        mid2Cia: '',
                        mid2Viva: '',
                        mid2Exam: '',
                        project: seedProject
                    });
                    continue;
                }
                students.push({
                    rollNo: activeRollNumbers[index - 1] || '',
                    attendance: index <= activeAttendance.length ? String(activeAttendance[index - 1]) : '',
                    mid1Obj: seedMid1Obj,
                    mid1Desc: '',
                    assignment1: activeEvaluationSheet === '1' ? seedAssignment : '',
                    mid2Obj: seedMid2Obj,
                    mid2Desc: activeEvaluationSheet === '1' ? '0' : '',
                    assignment2: activeEvaluationSheet === '1' ? seedAssignment : '',
                    assignment: activeEvaluationSheet === '1' ? seedAssignment : seedAssignment,
                    viva: seedViva
                });
            }
            return students;
        }

        function setGradeCell(cell, grade) {
            const label = grade || '-';
            cell.textContent = label;
            cell.dataset.grade = label;
        }

        function resetEvaluationMidTwoMarks(students) {
            return students.map(function (student) {
                return Object.assign({}, student, {
                    mid2Obj: '0',
                    mid2Desc: '0',
                    mid2Total: '0'
                });
            });
        }

        function parseScore(value) {
            const parsed = parseInt(value, 10);
            return Number.isNaN(parsed) ? 0 : parsed;
        }

        function parseAttendance(value) {
            const parsed = parseFloat(value);
            return Number.isNaN(parsed) ? 0 : parsed;
        }

        function getAttendanceGrade(attendance, maximumAttendance) {
            if (!maximumAttendance) return '-';
            const percentage = (attendance / maximumAttendance) * 100;
            if (percentage >= 90) return 'O';
            if (percentage >= 80) return 'A+';
            if (percentage >= 70) return 'A';
            if (percentage >= 60) return 'B+';
            if (percentage >= 50) return 'B';
            if (percentage >= 40) return 'P';
            return 'F';
        }

        function getMaximumAttendance() {
            const currentMarksBody = marksBodyMap[activeEvaluationSheet] || marksBodyMap['1'];
            const values = Array.from(currentMarksBody.querySelectorAll('.attendance'))
                .map(function (input) { return input.value.trim(); })
                .filter(Boolean)
                .map(parseAttendance);
            return values.length ? Math.max.apply(null, values) : 0;
        }

        function updateAttendanceGrades() {
            const currentMarksBody = marksBodyMap[activeEvaluationSheet] || marksBodyMap['1'];
            const maximumAttendance = getMaximumAttendance();
            currentMarksBody.querySelectorAll('tr').forEach(function (row) {
                const attendanceRaw = row.querySelector('.attendance').value.trim();
                const grade = attendanceRaw === '' ? '-' : getAttendanceGrade(parseAttendance(attendanceRaw), maximumAttendance);
                setGradeCell(row.querySelector('.attendance-grade'), grade);
            });
        }

        function predictAttendanceBasedDescriptiveMark(attendancePercentage, maximumDescription) {
            const boundedAttendance = Math.max(0, Math.min(100, parseAttendance(attendancePercentage)));
            return Math.max(0, Math.min(
                maximumDescription,
                Math.round(boundedAttendance * maximumDescription / 100)
            ));
        }

        function predictMidDescriptiveMarks(attendancePercentage, mid1Obj, assignment, viva) {
            // Evaluation 2 retains its lower MID-1 descriptive-mark cap.
            const mid1Maximum = activeEvaluationSheet === '2' ? 16 : 20;
            let mid1Desc = predictAttendanceBasedDescriptiveMark(attendancePercentage, mid1Maximum);

            function calculatedTotal() {
                const midAverage = Math.round((mid1Obj + mid1Desc) / 2);
                return Math.min(40, midAverage + assignment + viva);
            }

            const target = activeEvaluationSheet === '1' ? 32 : 30;

            // Preserve the attendance-based starting point, then add only the
            // marks needed to reach the target (75% class average) when the field maxima allow it.
            while (calculatedTotal() < target && mid1Desc < mid1Maximum) {
                mid1Desc += 1;
            }

            return { mid1Desc: mid1Desc, mid2Desc: 0, targetReached: calculatedTotal() >= target };
        }

        function recalculateEvaluationRow(row) {
            if (activeEvaluationSheet === '3' || activeEvaluationSheet === '4') {
                recalculateEvaluationThreeRow(row);
                return;
            }
            if (activeEvaluationSheet === '1') {
                recalculateEvaluationOneRow(row);
                return;
            }
            const mid1ObjInput = row.querySelector('.mid1-obj');
            const mid1DescInput = row.querySelector('.mid1-desc');
            const mid2ObjInput = row.querySelector('.mid2-obj');
            const mid2DescInput = row.querySelector('.mid2-desc');
            const isEditableEvaluationOne = activeEvaluationSheet === '1';
            const assignmentInput = row.querySelector('.assignment');
            const vivaInput = row.querySelector('.viva');
            let mid1ObjRaw = mid1ObjInput.value.trim();
            let mid2ObjRaw = mid2ObjInput.value.trim();
            let mid1DescRaw = mid1DescInput.value.trim();
            let mid2DescRaw = mid2DescInput.value.trim();
            let assignmentRaw = assignmentInput.value.trim();
            let vivaRaw = vivaInput.value.trim();

            if (mid1ObjRaw !== '' && mid1ObjRaw !== 'AB') mid1ObjInput.value = String(Math.max(0, Math.min(10, parseScore(mid1ObjRaw))));
            if (mid2ObjRaw !== '' && mid2ObjRaw !== 'AB') mid2ObjInput.value = String(Math.max(0, Math.min(10, parseScore(mid2ObjRaw))));
            if (isEditableEvaluationOne && mid1DescRaw !== '') mid1DescInput.value = String(Math.max(0, Math.min(20, parseScore(mid1DescRaw))));
            if (isEditableEvaluationOne && mid2DescRaw !== '') mid2DescInput.value = String(Math.max(0, Math.min(20, parseScore(mid2DescRaw))));
            if (assignmentRaw !== '') assignmentInput.value = String(Math.max(0, Math.min(5, parseScore(assignmentRaw))));
            if (vivaRaw !== '') vivaInput.value = String(Math.max(0, Math.min(5, parseScore(vivaRaw))));

            mid1ObjRaw = mid1ObjInput.value.trim();
            mid2ObjRaw = mid2ObjInput.value.trim();
            assignmentRaw = assignmentInput.value.trim();
            vivaRaw = vivaInput.value.trim();
            const hasAllPredictionInputs = [mid1ObjRaw, mid2ObjRaw, assignmentRaw, vivaRaw].every(Boolean);

            if (!isEditableEvaluationOne && hasAllPredictionInputs) {
                const prediction = predictMidDescriptiveMarks(
                    row.querySelector('.attendance').value,
                    parseScore(mid1ObjRaw),
                    parseScore(assignmentRaw),
                    parseScore(vivaRaw)
                );
                mid1DescInput.value = String(prediction.mid1Desc);
                mid2DescInput.value = '0';
                row.dataset.targetReached = prediction.targetReached ? 'true' : 'false';
            } else if (!isEditableEvaluationOne) {
                mid1DescInput.value = '';
                mid2DescInput.value = '0';
                delete row.dataset.targetReached;
            }

            mid1DescRaw = mid1DescInput.value.trim();
            mid2DescRaw = mid2DescInput.value.trim();

            const hasAnyMarks = [mid1ObjRaw, mid1DescRaw, mid2ObjRaw, mid2DescRaw, assignmentRaw, vivaRaw].some(Boolean);

            if (!hasAnyMarks) {
                row.querySelector('.mid1-total').textContent = '-';
                row.querySelector('.mid2-total').textContent = '0';
                row.querySelector('.mid-avg').textContent = '-';
                row.querySelector('.total').textContent = '-';
                const pctCell = row.querySelector('.percentage');
                if (pctCell) pctCell.textContent = '-';
                setGradeCell(row.querySelector('.grade'), '-');
                return;
            }

            const mid1Obj = parseScore(mid1ObjRaw);
            const mid1Desc = parseScore(mid1DescRaw);
            const assignment = parseScore(assignmentRaw);
            const viva = parseScore(vivaRaw);

            const mid1Total = mid1Obj + mid1Desc;
            const mid2Total = isEditableEvaluationOne
                ? parseScore(mid2ObjRaw) + parseScore(mid2DescRaw) : 0;
            const midAvg = Math.round((mid1Total + mid2Total) / 2);
            const total = Math.min(midAvg + assignment + viva, 40);

            row.querySelector('.mid1-total').textContent = String(mid1Total);
            row.querySelector('.mid2-total').textContent = String(mid2Total);
            row.querySelector('.mid-avg').textContent = String(midAvg);
            const totalCell = row.querySelector('.total');
            totalCell.textContent = String(total);
            if (!isEditableEvaluationOne && hasAllPredictionInputs) {
                const targetReached = row.dataset.targetReached === 'true';
                totalCell.title = targetReached
                    ? 'Automatically calculated total; the 75% target is satisfied.'
                    : 'The 75% target cannot be reached with these inputs, even at the allowed descriptive-mark maxima.';
                totalCell.classList.toggle('text-danger', !targetReached);
                 totalCell.classList.toggle('fw-bold', !targetReached);
            } else {
                totalCell.removeAttribute('title');
                totalCell.classList.remove('text-danger', 'fw-bold');
            }
            setGradeCell(row.querySelector('.grade'), getGrade(total));

            const percentageCell = row.querySelector('.percentage');
            if (percentageCell) {
                const percentage = (total / 40 * 100).toFixed(1);
                percentageCell.textContent = percentage + '%';
                percentageCell.classList.toggle('text-success', total >= 30);
                percentageCell.classList.toggle('text-danger', total < 30 && total !== 0);
            }
        }

        function recalculateEvaluationOneRow(row) {
            function parseMark(value, max) {
                if (value === '' || value === undefined || value === null) return null;
                if (String(value).trim().toUpperCase() === 'AB') return null;
                const parsed = parseFloat(String(value).trim());
                if (isNaN(parsed)) return null;
                return Math.max(0, Math.min(max, parsed));
            }
            function formatMark(value) {
                if (value === null || value === undefined || value === '') return '';
                const num = Number(value);
                if (isNaN(num)) return String(value);
                if (Number.isInteger(num)) return String(num);
                return String(parseFloat(num.toFixed(2)));
            }

            const mid1ObjInput = row.querySelector('.mid1-obj');
            const mid1DescInput = row.querySelector('.mid1-desc');
            const assignment1Input = row.querySelector('.assignment1');
            const mid2ObjInput = row.querySelector('.mid2-obj');
            const mid2DescInput = row.querySelector('.mid2-desc');
            const assignment2Input = row.querySelector('.assignment2');
            const vivaInput = row.querySelector('.viva');

            const mid1Obj = parseMark(mid1ObjInput.value, 10);
            const mid1Desc = parseMark(mid1DescInput.value, 20);
            const assignment1 = parseMark(assignment1Input.value, 5);
            const mid2Obj = parseMark(mid2ObjInput.value, 10);
            const mid2Desc = parseMark(mid2DescInput.value, 20);
            const assignment2 = parseMark(assignment2Input.value, 5);
            const viva = parseMark(vivaInput.value, 5);

            if (mid1ObjInput.value.trim() !== '' && mid1ObjInput.value.trim().toUpperCase() !== 'AB' && mid1Obj !== null) mid1ObjInput.value = formatMark(mid1Obj);
            if (mid1DescInput.value.trim() !== '' && mid1Desc !== null) mid1DescInput.value = formatMark(mid1Desc);
            if (assignment1Input.value.trim() !== '' && assignment1 !== null) assignment1Input.value = formatMark(assignment1);
            if (mid2ObjInput.value.trim() !== '' && mid2ObjInput.value.trim().toUpperCase() !== 'AB' && mid2Obj !== null) mid2ObjInput.value = formatMark(mid2Obj);
            if (mid2DescInput.value.trim() !== '' && mid2Desc !== null) mid2DescInput.value = formatMark(mid2Desc);
            if (assignment2Input.value.trim() !== '' && assignment2 !== null) assignment2Input.value = formatMark(assignment2);
            if (vivaInput.value.trim() !== '' && viva !== null) vivaInput.value = formatMark(viva);

            const inputs = [mid1ObjInput, mid1DescInput, assignment1Input, mid2ObjInput, mid2DescInput, assignment2Input, vivaInput];
            const hasAnyMarks = inputs.some(function (input) { return input && input.value.trim() !== ''; });

            if (!hasAnyMarks) {
                row.querySelector('.mid1-total').textContent = '-';
                row.querySelector('.mid2-total').textContent = '-';
                row.querySelector('.mid-avg').textContent = '-';
                row.querySelector('.assignment-avg').textContent = '-';
                row.querySelector('.total').textContent = '-';
                const pctCell = row.querySelector('.percentage');
                if (pctCell) pctCell.textContent = '-';
                setGradeCell(row.querySelector('.grade'), '-');
                return;
            }

            const mid1Total = (mid1Obj || 0) + (mid1Desc || 0);
            const mid2Total = (mid2Obj || 0) + (mid2Desc || 0);
            const midAvg = Math.round((mid1Total + mid2Total) / 2);
            const assignmentAvg = ((assignment1 || 0) + (assignment2 || 0)) / 2;
            const rawTotal = midAvg + assignmentAvg + (viva || 0);
            const total = Math.min(Math.ceil(rawTotal), 40);

            row.querySelector('.mid1-total').textContent = String(mid1Total);
            row.querySelector('.mid2-total').textContent = String(mid2Total);
            row.querySelector('.mid-avg').textContent = String(midAvg);
            row.querySelector('.assignment-avg').textContent = formatMark(assignmentAvg);
            const totalCell = row.querySelector('.total');
            totalCell.textContent = String(total);
            totalCell.removeAttribute('title');
            totalCell.classList.remove('text-danger', 'fw-bold');
            setGradeCell(row.querySelector('.grade'), getGrade(total));

            const percentageCell = row.querySelector('.percentage');
            if (percentageCell) {
                const percentage = (total / 40 * 100).toFixed(1);
                percentageCell.textContent = percentage + '%';
                percentageCell.classList.toggle('text-success', total >= 30);
                percentageCell.classList.toggle('text-danger', total < 30 && total !== 0);
            }
        }

        function recalculateEvaluationThreeRow(row) {
            const mid1CiaInput = row.querySelector('.mid1-cia');
            const mid1VivaInput = row.querySelector('.mid1-viva');
            const mid1ExamInput = row.querySelector('.mid1-exam');
            const mid2CiaInput = row.querySelector('.mid2-cia');
            const mid2VivaInput = row.querySelector('.mid2-viva');
            const mid2ExamInput = row.querySelector('.mid2-exam');
            const projectInput = row.querySelector('.project');

            [mid1CiaInput, mid1VivaInput, mid1ExamInput, mid2CiaInput, mid2VivaInput, mid2ExamInput, projectInput].forEach(function (input) {
                if (!input) return;
                const raw = input.value.trim();
                if (raw !== '') input.value = String(Math.max(0, Math.min(10, parseScore(raw))));
            });

            const mid1Cia = parseScore(mid1CiaInput ? mid1CiaInput.value : '');
            const mid1Viva = parseScore(mid1VivaInput ? mid1VivaInput.value : '');
            const mid1Exam = parseScore(mid1ExamInput ? mid1ExamInput.value : '');
            const mid2Cia = parseScore(mid2CiaInput ? mid2CiaInput.value : '');
            const mid2Viva = parseScore(mid2VivaInput ? mid2VivaInput.value : '');
            const mid2Exam = parseScore(mid2ExamInput ? mid2ExamInput.value : '');
            const project = parseScore(projectInput ? projectInput.value : '');

            const mid1Total = Math.min(30, mid1Cia + mid1Viva + mid1Exam);
            const mid2Total = Math.min(30, mid2Cia + mid2Viva + mid2Exam);
            const midAvg = Math.round((mid1Total + mid2Total) / 2);
            const total = Math.min(40, midAvg + project);
            const hasMarks = [mid1CiaInput, mid1VivaInput, mid1ExamInput, mid2CiaInput,
                mid2VivaInput, mid2ExamInput, projectInput].some(function (input) {
                    return input && input.value.trim() !== '';
                });

            row.querySelector('.mid1-total').textContent = String(mid1Total);
            row.querySelector('.mid2-total').textContent = String(mid2Total);
            row.querySelector('.mid-avg').textContent = String(midAvg);
            const totalCell = row.querySelector('.total');
            totalCell.textContent = String(total);
            totalCell.classList.remove('text-danger', 'fw-bold');
            if (total < 14) {
                totalCell.classList.add('text-danger', 'fw-bold');
            }
            setGradeCell(row.querySelector('.grade'),
                (activeEvaluationSheet === '3' || activeEvaluationSheet === '4') && !hasMarks ? '-' : getGrade(total));
            if (activeEvaluationSheet === '3' || activeEvaluationSheet === '4') {
                const extCell = row.querySelector('.external-eval');
                const writeupCell = row.querySelector('.ext-writeup');
                const experimentCell = row.querySelector('.ext-experiment');
                const evalResultsCell = row.querySelector('.ext-evaluation-results');
                const presentationCell = row.querySelector('.ext-presentation');
                const vivaCell = row.querySelector('.ext-viva');
                const totalIntExtCell = row.querySelector('.total-int-ext');
                if (hasMarks) {
                    const ext = Math.min(60, Math.max(Math.round(total * 60 / 40 + 3), Math.max(0, 40 - total)));
                    if (extCell) extCell.textContent = String(ext);
                    const w = Math.min(10, Math.max(1, ext - 4));
                    const eprog = Math.min(15, Math.max(1, ext - w - 3));
                    const eres = Math.min(15, Math.max(1, ext - w - eprog - 2));
                    const pres = Math.min(10, Math.max(1, ext - w - eprog - eres - 1));
                    const vivaE = ext - w - eprog - eres - pres;
                    if (writeupCell) writeupCell.textContent = String(w);
                    if (experimentCell) experimentCell.textContent = String(eprog);
                    if (evalResultsCell) evalResultsCell.textContent = String(eres);
                    if (presentationCell) presentationCell.textContent = String(pres);
                    if (vivaCell) vivaCell.textContent = String(vivaE);
                    if (totalIntExtCell) totalIntExtCell.textContent = String(total + ext);
                } else {
                    if (extCell) extCell.textContent = '-';
                    if (writeupCell) writeupCell.textContent = '-';
                    if (experimentCell) experimentCell.textContent = '-';
                    if (evalResultsCell) evalResultsCell.textContent = '-';
                    if (presentationCell) presentationCell.textContent = '-';
                    if (vivaCell) vivaCell.textContent = '-';
                    if (totalIntExtCell) totalIntExtCell.textContent = '-';
                }
            }

            if (activeEvaluationSheet === '3') {
                updateEvaluationThreeMid1Average();
                updateEvaluationThreeMid2Average();
                updateEvaluationThreeTotalAverage();
            } else if (activeEvaluationSheet === '4') {
                updateEvaluationFourMid1Average();
                updateEvaluationFourMid2Average();
                updateEvaluationFourTotalAverage();
            }
        }

        function setupEvaluationHorizontalScrollbar(section) {
            if (!section) return;
            const scrollContainer = section.querySelector('.evaluation-marks-scroll');
            const table = scrollContainer ? scrollContainer.querySelector('table[id^="internalMarksTable"]') : null;
            if (!scrollContainer || !table) return;
            scrollContainer.setAttribute('tabindex', '0');
            scrollContainer.setAttribute('role', 'region');
            scrollContainer.setAttribute('aria-label', 'Student marks; scroll vertically and horizontally');

            let horizontalScrollbar = section.querySelector('.evaluation-horizontal-scroll');
            if (!horizontalScrollbar) {
                horizontalScrollbar = document.createElement('div');
                horizontalScrollbar.className = 'evaluation-horizontal-scroll';
                horizontalScrollbar.setAttribute('role', 'region');
                horizontalScrollbar.setAttribute('aria-label', 'Scroll marks table horizontally');
                horizontalScrollbar.setAttribute('tabindex', '0');
                const scrollbarContent = document.createElement('div');
                scrollbarContent.className = 'evaluation-horizontal-scroll-content';
                scrollbarContent.setAttribute('aria-hidden', 'true');
                horizontalScrollbar.appendChild(scrollbarContent);
                scrollContainer.parentNode.insertBefore(horizontalScrollbar, scrollContainer);

                horizontalScrollbar.addEventListener('scroll', function () {
                    if (scrollContainer.scrollLeft !== horizontalScrollbar.scrollLeft) {
                        scrollContainer.scrollLeft = horizontalScrollbar.scrollLeft;
                    }
                });
                scrollContainer.addEventListener('scroll', function () {
                    if (horizontalScrollbar.scrollLeft !== scrollContainer.scrollLeft) {
                        horizontalScrollbar.scrollLeft = scrollContainer.scrollLeft;
                    }
                });
            }

            const scrollbarContent = horizontalScrollbar.firstElementChild;
            const updateScrollbar = function () {
                scrollbarContent.style.width = table.scrollWidth + 'px';
                horizontalScrollbar.hidden = table.scrollWidth <= scrollContainer.clientWidth;
                horizontalScrollbar.scrollLeft = scrollContainer.scrollLeft;
            };
            updateScrollbar();
            if (typeof ResizeObserver !== 'undefined' && !horizontalScrollbar.dataset.resizeObserved) {
                const resizeObserver = new ResizeObserver(updateScrollbar);
                resizeObserver.observe(scrollContainer);
                resizeObserver.observe(table);
                horizontalScrollbar.dataset.resizeObserved = 'true';
            }
        }

        function renderStudents(students) {
            const currentMarksBody = marksBodyMap[activeEvaluationSheet] || marksBodyMap['1'];
            const evaluationThreeMarkInputType = activeEvaluationSheet === '3' ? 'text' : 'number';
            const evaluationThreeMarkInputMode = activeEvaluationSheet === '3'
                ? ' inputmode="numeric" pattern="[0-9]*"' : '';
            if (activeEvaluationSheet === '2') {
                students = resetEvaluationMidTwoMarks(students);
            }
            currentMarksBody.innerHTML = '';

            students.forEach(function (student) {
                const row = document.createElement('tr');
                if (activeEvaluationSheet === '3' || activeEvaluationSheet === '4') {
                    const rollNumberAttributes = activeEvaluationSheet === '3'
                        ? ' readonly title="Linked automatically from Internal Evaluation 1"' : '';
                    row.innerHTML = ''
                        + '<td><input type="text" class="form-control form-control-sm roll-no" value="' + (student.rollNo || '') + '"' + rollNumberAttributes + ' /></td>'
                        + '<td><input type="text" class="form-control form-control-sm attendance" value="' + (student.attendance ?? '') + '" pattern="[0-9]*"></td>'
                        + '<td class="attendance-grade" data-grade="-">-</td>'
                        + '<td><input type="' + evaluationThreeMarkInputType + '"' + evaluationThreeMarkInputMode + ' min="0" max="10" step="1" class="form-control form-control-sm mid1-cia" value="' + (student.mid1Cia || '') + '"></td>'
                        + '<td><input type="' + evaluationThreeMarkInputType + '"' + evaluationThreeMarkInputMode + ' min="0" max="10" step="1" class="form-control form-control-sm mid1-viva" value="' + (student.mid1Viva || '') + '"></td>'
                        + '<td><input type="' + evaluationThreeMarkInputType + '"' + evaluationThreeMarkInputMode + ' min="0" max="10" step="1" class="form-control form-control-sm mid1-exam" value="' + (student.mid1Exam || '') + '"></td>'
                        + '<td class="mid1-total">-</td>'
                        + '<td><input type="' + evaluationThreeMarkInputType + '"' + evaluationThreeMarkInputMode + ' min="0" max="10" step="1" class="form-control form-control-sm mid2-cia" value="' + (student.mid2Cia || '') + '"></td>'
                        + '<td><input type="' + evaluationThreeMarkInputType + '"' + evaluationThreeMarkInputMode + ' min="0" max="10" step="1" class="form-control form-control-sm mid2-viva" value="' + (student.mid2Viva || '') + '"></td>'
                        + '<td><input type="' + evaluationThreeMarkInputType + '"' + evaluationThreeMarkInputMode + ' min="0" max="10" step="1" class="form-control form-control-sm mid2-exam" value="' + (student.mid2Exam || '') + '"></td>'
                        + '<td class="mid2-total">-</td>'
                        + '<td class="mid-avg">-</td>'
                        + '<td><input type="' + evaluationThreeMarkInputType + '"' + evaluationThreeMarkInputMode + ' min="0" max="10" step="1" class="form-control form-control-sm project" value="' + (student.project || '') + '"></td>'
                        + '<td class="total">-</td>'
                        + '<td class="grade" data-grade="-">-</td>'
                        + ((activeEvaluationSheet === '3' || activeEvaluationSheet === '4')
                            ? '<td class="external-eval">-</td><td class="ext-writeup">-</td><td class="ext-experiment">-</td><td class="ext-evaluation-results">-</td><td class="ext-presentation">-</td><td class="ext-viva">-</td><td class="total-int-ext">-</td>'
                            : '');
                } else if (activeEvaluationSheet === '1') {
                    row.innerHTML = ''
                        + '<td><input type="text" class="form-control form-control-sm roll-no" value="' + (student.rollNo || '') + '" /></td>'
                        + '<td><input type="text" class="form-control form-control-sm attendance" value="' + (student.attendance ?? '') + '" pattern="[0-9]*"></td>'
                        + '<td class="attendance-grade" data-grade="-">-</td>'
                        + '<td><input type="text" class="form-control form-control-sm mid1-obj" value="' + (student.mid1Obj || '') + '"></td>'
                        + '<td><input type="text" inputmode="decimal" class="form-control form-control-sm mid1-desc" value="' + (student.mid1Desc || '') + '"></td>'
                        + '<td><input type="text" inputmode="decimal" class="form-control form-control-sm assignment1" value="' + (student.assignment1 ?? '') + '"></td>'
                        + '<td class="mid1-total">-</td>'
                        + '<td><input type="text" class="form-control form-control-sm mid2-obj" value="' + (student.mid2Obj || '') + '"></td>'
                        + '<td><input type="text" inputmode="decimal" class="form-control form-control-sm mid2-desc" value="' + (student.mid2Desc || '') + '"></td>'
                        + '<td><input type="text" inputmode="decimal" class="form-control form-control-sm assignment2" value="' + (student.assignment2 ?? '') + '"></td>'
                        + '<td class="mid2-total">-</td>'
                        + '<td class="mid-avg">-</td>'
                        + '<td class="assignment-avg">-</td>'
                        + '<td><input type="text" inputmode="decimal" class="form-control form-control-sm viva" value="' + (student.viva || '') + '"></td>'
                        + '<td class="total">-</td>'
                        + '<td class="percentage">-</td>'
                        + '<td class="grade" data-grade="-">-</td>';
                } else {
                    row.innerHTML = ''
                        + '<td><input type="text" class="form-control form-control-sm roll-no" value="' + (student.rollNo || '') + '" /></td>'
                        + '<td><input type="text" class="form-control form-control-sm attendance" value="' + (student.attendance ?? '') + '" pattern="[0-9]*"></td>'
                        + '<td class="attendance-grade" data-grade="-">-</td>'
                        + '<td><input type="text" class="form-control form-control-sm mid1-obj" value="' + (student.mid1Obj || '') + '"></td>'
                        + '<td><input type="text" inputmode="numeric" pattern="[0-9]*" class="form-control form-control-sm mid1-desc" value="' + (student.mid1Desc || '') + '"></td>'
                        + '<td class="mid1-total">-</td>'
                        + '<td><input type="text" class="form-control form-control-sm mid2-obj" value="' + (student.mid2Obj || '') + '"></td>'
                        + '<td><input type="text" inputmode="numeric" pattern="[0-9]*" class="form-control form-control-sm mid2-desc" value="' + (student.mid2Desc || '') + '"></td>'
                        + '<td class="mid2-total">-</td>'
                        + '<td class="mid-avg">-</td>'
                        + '<td><input type="text" inputmode="numeric" pattern="[0-9]*" class="form-control form-control-sm assignment" value="' + (student.assignment || '') + '"></td>'
                        + '<td><input type="text" inputmode="numeric" pattern="[0-9]*" class="form-control form-control-sm viva" value="' + (student.viva || '') + '"></td>'
                        + '<td class="total">-</td>'
                        + '<td class="percentage">-</td>'
                        + '<td class="grade" data-grade="-">-</td>';
                }
                currentMarksBody.appendChild(row);
                if (activeEvaluationSheet === '1') {
                    row.querySelectorAll('.mid1-obj, .mid1-desc, .assignment1, .mid2-obj, .mid2-desc, .assignment2, .viva').forEach(function (input) {
                        input.readOnly = false;
                        input.disabled = false;
                        input.removeAttribute('readonly');
                        input.removeAttribute('disabled');
                    });
                } else {
                    row.querySelectorAll('.mid1-desc, .mid2-desc, .assignment, .viva').forEach(function (input) {
                        input.type = 'text';
                        input.setAttribute('inputmode', 'numeric');
                        input.setAttribute('pattern', '[0-9]*');
                        input.readOnly = activeEvaluationSheet !== '1';
                        input.disabled = false;
                        if (activeEvaluationSheet === '1') {
                            input.removeAttribute('readonly');
                            input.removeAttribute('disabled');
                        } else {
                            input.title = 'Automatically predicted from attendance when Obj, Assignment and Viva marks are entered';
                        }
                    });
                }
                if (activeEvaluationSheet === '3') {
                    row.querySelectorAll('.mid1-cia, .mid1-viva, .mid1-exam, .mid2-cia, .mid2-viva, .mid2-exam, .project')
                        .forEach(function (input) {
                            input.type = 'text';
                            input.setAttribute('inputmode', 'numeric');
                            input.setAttribute('pattern', '[0-9]*');
                        });
                }
                recalculateEvaluationRow(row);
            });

            updateAttendanceGrades();
            updateGradeSummary();
            updateEvaluationMetrics();
            updateAllEvaluationAverages();
            setupEvaluationHorizontalScrollbar(currentMarksBody.closest('.evaluation-section'));
        }

        function getEvaluationRows(sheetNumber) {
            const evaluationNumber = sheetNumber || activeEvaluationSheet;
            const currentMarksBody = marksBodyMap[evaluationNumber] || marksBodyMap['1'];
            return Array.from(currentMarksBody.querySelectorAll('tr')).map(function (row) {
                if (evaluationNumber === '3' || evaluationNumber === '4') {
                    return {
                        rollNo: row.querySelector('.roll-no') ? row.querySelector('.roll-no').value : '',
                        attendance: row.querySelector('.attendance') ? row.querySelector('.attendance').value : '',
                        attendanceGrade: row.querySelector('.attendance-grade') ? row.querySelector('.attendance-grade').textContent : '-',
                        mid1Cia: row.querySelector('.mid1-cia') ? row.querySelector('.mid1-cia').value : '',
                        mid1Viva: row.querySelector('.mid1-viva') ? row.querySelector('.mid1-viva').value : '',
                        mid1Exam: row.querySelector('.mid1-exam') ? row.querySelector('.mid1-exam').value : '',
                        mid1Total: row.querySelector('.mid1-total') ? row.querySelector('.mid1-total').textContent : '-',
                        mid2Cia: row.querySelector('.mid2-cia') ? row.querySelector('.mid2-cia').value : '',
                        mid2Viva: row.querySelector('.mid2-viva') ? row.querySelector('.mid2-viva').value : '',
                        mid2Exam: row.querySelector('.mid2-exam') ? row.querySelector('.mid2-exam').value : '',
                        mid2Total: row.querySelector('.mid2-total') ? row.querySelector('.mid2-total').textContent : '-',
                        midAvg: row.querySelector('.mid-avg') ? row.querySelector('.mid-avg').textContent : '-',
                        project: row.querySelector('.project') ? row.querySelector('.project').value : '',
                        total: row.querySelector('.total') ? row.querySelector('.total').textContent : '-',
                        grade: row.querySelector('.grade') ? row.querySelector('.grade').textContent : '-'
                    };
                }
                if (evaluationNumber === '1') {
                    const assignment1Val = row.querySelector('.assignment1') ? row.querySelector('.assignment1').value : '';
                    const assignment2Val = row.querySelector('.assignment2') ? row.querySelector('.assignment2').value : '';
                    const assignmentAvgVal = row.querySelector('.assignment-avg') ? row.querySelector('.assignment-avg').textContent : '-';
                    return {
                        rollNo: row.querySelector('.roll-no') ? row.querySelector('.roll-no').value : '',
                        attendance: row.querySelector('.attendance') ? row.querySelector('.attendance').value : '',
                        attendanceGrade: row.querySelector('.attendance-grade') ? row.querySelector('.attendance-grade').textContent : '-',
                        mid1Obj: row.querySelector('.mid1-obj') ? row.querySelector('.mid1-obj').value : '',
                        mid1Desc: row.querySelector('.mid1-desc') ? row.querySelector('.mid1-desc').value : '',
                        assignment1: assignment1Val,
                        mid2Obj: row.querySelector('.mid2-obj') ? row.querySelector('.mid2-obj').value : '',
                        mid2Desc: row.querySelector('.mid2-desc') ? row.querySelector('.mid2-desc').value : '',
                        assignment2: assignment2Val,
                        assignment: assignmentAvgVal,
                        viva: row.querySelector('.viva') ? row.querySelector('.viva').value : '',
                        total: row.querySelector('.total') ? row.querySelector('.total').textContent : '-',
                        percentage: row.querySelector('.percentage') ? row.querySelector('.percentage').textContent : '-',
                        grade: row.querySelector('.grade') ? row.querySelector('.grade').textContent : '-'
                    };
                }
                return {
                    rollNo: row.querySelector('.roll-no') ? row.querySelector('.roll-no').value : '',
                    attendance: row.querySelector('.attendance') ? row.querySelector('.attendance').value : '',
                    attendanceGrade: row.querySelector('.attendance-grade') ? row.querySelector('.attendance-grade').textContent : '-',
                    mid1Obj: row.querySelector('.mid1-obj') ? row.querySelector('.mid1-obj').value : '',
                    mid1Desc: row.querySelector('.mid1-desc') ? row.querySelector('.mid1-desc').value : '',
                    mid2Obj: row.querySelector('.mid2-obj') ? row.querySelector('.mid2-obj').value : '',
                    mid2Desc: row.querySelector('.mid2-desc') ? row.querySelector('.mid2-desc').value : '',
                    assignment: row.querySelector('.assignment') ? row.querySelector('.assignment').value : '',
                    viva: row.querySelector('.viva') ? row.querySelector('.viva').value : '',
                    total: row.querySelector('.total') ? row.querySelector('.total').textContent : '-',
                    percentage: row.querySelector('.percentage') ? row.querySelector('.percentage').textContent : '-',
                    grade: row.querySelector('.grade') ? row.querySelector('.grade').textContent : '-'
                };
            });
        }

        function hasEvaluationContent() {
            return getEvaluationRows().some(function (student) {
                if (activeEvaluationSheet === '3' || activeEvaluationSheet === '4') {
                    return student.rollNo.trim()
                        || student.attendance.trim()
                        || student.mid1Cia.trim()
                        || student.mid1Viva.trim()
                        || student.mid1Exam.trim()
                        || student.mid2Cia.trim()
                        || student.mid2Viva.trim()
                        || student.mid2Exam.trim()
                        || student.project.trim();
                }
                if (evaluationNumber === '1') {
                    return student.rollNo.trim()
                        || student.attendance.trim()
                        || student.mid1Obj.trim()
                        || student.mid1Desc.trim()
                        || (student.assignment1 && String(student.assignment1).trim())
                        || student.mid2Obj.trim()
                        || student.mid2Desc.trim()
                        || (student.assignment2 && String(student.assignment2).trim())
                        || student.viva.trim();
                }
                return student.rollNo.trim()
                    || student.attendance.trim()
                    || student.mid1Obj.trim()
                    || student.mid1Desc.trim()
                    || student.mid2Obj.trim()
                    || student.mid2Desc.trim()
                    || student.assignment.trim()
                    || student.viva.trim();
            });
        }

        function getGrade(total) {
            if (total >= 37) return 'O';
            if (total >= 32) return 'A+';
            if (total >= 28) return 'A';
            if (total >= 24) return 'B+';
            if (total >= 20) return 'B';
            if (total >= 14) return 'P';
            return 'F';
        }

        function calculateGradeDistribution(students) {
            const grades = {
                'O': { count: 0, rolls: [] },
                'A+': { count: 0, rolls: [] },
                'A': { count: 0, rolls: [] },
                'B+': { count: 0, rolls: [] },
                'B': { count: 0, rolls: [] },
                'P': { count: 0, rolls: [] },
                'F': { count: 0, rolls: [] }
            };

            students.forEach(function (student) {
                if (!student.grade || student.grade === '-' || student.grade === 'ABSENT') {
                    return;
                }

                grades[student.grade].count += 1;
                if ((student.rollNo || '').trim()) {
                    grades[student.grade].rolls.push(student.rollNo.trim());
                }
            });

            return grades;
        }

        function calculateAttendanceGradeDistribution(students) {
            const grades = {
                'O': { count: 0, rolls: [] },
                'A+': { count: 0, rolls: [] },
                'A': { count: 0, rolls: [] },
                'B+': { count: 0, rolls: [] },
                'B': { count: 0, rolls: [] },
                'P': { count: 0, rolls: [] },
                'F': { count: 0, rolls: [] }
            };

            students.forEach(function (student) {
                if (!grades[student.attendanceGrade]) return;
                grades[student.attendanceGrade].count += 1;
                if ((student.rollNo || '').trim()) {
                    grades[student.attendanceGrade].rolls.push(student.rollNo.trim());
                }
            });
            return grades;
        }

        function calculateDistributedAttendanceGrades(students) {
            const grades = {
                'O': { students: [], allocatedPercentage: 0 },
                'A+': { students: [], allocatedPercentage: 0 },
                'A': { students: [], allocatedPercentage: 0 },
                'B+': { students: [], allocatedPercentage: 0 },
                'B': { students: [], allocatedPercentage: 0 },
                'P': { students: [], allocatedPercentage: 0 },
                'F': { students: [], allocatedPercentage: 0 }
            };
            const maximumAttendance = getMaximumAttendance();
            const rankedStudents = students
                .filter(function (student) { return String(student.attendance || '').trim() !== ''; })
                .map(function (student, index) {
                    const attendance = parseAttendance(student.attendance);
                    return Object.assign({}, student, {
                        originalIndex: index,
                        attendanceValue: attendance,
                        attendancePercentage: maximumAttendance ? (attendance / maximumAttendance) * 100 : 0
                    });
                })
                .sort(function (first, second) {
                    return second.attendancePercentage - first.attendancePercentage
                        || first.originalIndex - second.originalIndex;
                });

            if (!rankedStudents.length) return grades;

            const allocationGroups = [
                { grade: 'O', percentage: 15 },
                { grade: 'A+', percentage: 25 },
                { grade: 'A', percentage: 25 },
                { grade: 'B+', percentage: 25 },
                { grade: 'LOWER', percentage: 10 }
            ];
            const exactCounts = allocationGroups.map(function (group) {
                return rankedStudents.length * group.percentage / 100;
            });
            const allocatedCounts = exactCounts.map(Math.floor);
            let unallocatedCount = rankedStudents.length - allocatedCounts.reduce(function (sum, count) {
                return sum + count;
            }, 0);
            exactCounts
                .map(function (exactCount, index) {
                    return { index: index, remainder: exactCount - allocatedCounts[index] };
                })
                .sort(function (first, second) {
                    return second.remainder - first.remainder || first.index - second.index;
                })
                .forEach(function (item) {
                    if (unallocatedCount > 0) {
                        allocatedCounts[item.index] += 1;
                        unallocatedCount -= 1;
                    }
                });

            let cursor = 0;
            allocationGroups.forEach(function (group, index) {
                const selectedStudents = rankedStudents.slice(cursor, cursor + allocatedCounts[index]);
                cursor += allocatedCounts[index];
                if (group.grade !== 'LOWER') {
                    grades[group.grade].students = selectedStudents;
                    return;
                }
                selectedStudents.forEach(function (student) {
                    const lowerGrade = getAttendanceGrade(student.attendanceValue, maximumAttendance);
                    grades[['B', 'P', 'F'].includes(lowerGrade) ? lowerGrade : 'B'].students.push(student);
                });
            });

            Object.keys(grades).forEach(function (grade) {
                grades[grade].allocatedPercentage = grades[grade].students.length / rankedStudents.length * 100;
            });
            return grades;
        }

        function updateEvaluationMetrics() {
            const students = getEvaluationRows();
            const gradedStudents = students.filter(function (student) {
                return student.grade && student.grade !== '-' && student.grade !== 'ABSENT';
            });
            const distribution = calculateGradeDistribution(students);
            const gradeOrder = ['O', 'A+', 'A', 'B+', 'B', 'P', 'F'];
            const classAverageStudents = activeEvaluationSheet === '3' ? gradedStudents : students;

            const averageTotal = gradedStudents.length
                ? (gradedStudents.reduce(function (sum, student) {
                    return sum + parseScore(student.total);
                }, 0) / gradedStudents.length).toFixed(1)
                : '0.0';

            const passRate = gradedStudents.length
                ? Math.round((gradedStudents.filter(function (student) { return parseScore(student.total) >= 14; }).length / gradedStudents.length) * 100) + '%'
                : '0%';

            const highestGrade = gradeOrder.find(function (grade) {
                return distribution[grade].count > 0;
            }) || '-';

            document.getElementById('evaluationGeneratedCount').textContent = String(students.length);
            document.getElementById('evaluationAverageMark').textContent = averageTotal;
            document.getElementById('evaluationPassRate').textContent = passRate;
            document.getElementById('evaluationTopGrade').textContent = highestGrade;

            var classAveragePercentageEl = document.getElementById('evaluationClassAveragePercentage');
            if (classAveragePercentageEl && classAverageStudents.length) {
                var totalAll = classAverageStudents.reduce(function (sum, student) { return sum + parseScore(student.total); }, 0);
                var classAvgPercentage = (totalAll / (classAverageStudents.length * 40) * 100).toFixed(1);
                classAveragePercentageEl.textContent = classAvgPercentage + '%';
                classAveragePercentageEl.parentElement.classList.toggle('insight-card-success', parseFloat(classAvgPercentage) >= 75);
                classAveragePercentageEl.parentElement.classList.toggle('insight-card-warning', parseFloat(classAvgPercentage) < 75);
            } else if (classAveragePercentageEl) {
                classAveragePercentageEl.textContent = '0.0%';
            }

            updateEvaluationOneMid1Average();
            updateEvaluationOneMid2Average();
            updateEvaluationOneTotalAverage();
        }

        function updateEvaluationOneMid1Average() {
            const averageInput = document.getElementById('evaluationOneMid1Average');
            const averageNote = document.getElementById('evaluationOneMid1AverageNote');
            const evaluationOneMarksBody = marksBodyMap['1'];
            if (!averageInput || !averageNote || !evaluationOneMarksBody) return;

            const completedMidOneTotals = Array.from(evaluationOneMarksBody.querySelectorAll('tr'))
                .map(function (row) { return row.querySelector('.mid1-total').textContent.trim(); })
                .filter(function (total) { return total !== '-' && total !== ''; })
                .map(parseScore);
            const averageAchieved = completedMidOneTotals.length
                ? completedMidOneTotals.reduce(function (sum, total) { return sum + total; }, 0)
                    / (completedMidOneTotals.length * 30) * 100
                : 0;
            const isAtOrAboveLimit = averageAchieved >= 75;

            averageInput.value = averageAchieved.toFixed(1) + '%';
            averageInput.classList.toggle('is-invalid', isAtOrAboveLimit);
            averageInput.classList.toggle('is-valid', completedMidOneTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.textContent = !completedMidOneTotals.length
                ? 'No MID-1 totals entered yet'
                : (isAtOrAboveLimit
                    ? 'At or above 75% — reduce MID-1 marks'
                    : 'Below 75% — requirement met');
            averageNote.classList.toggle('text-danger', isAtOrAboveLimit);
            averageNote.classList.toggle('text-success', completedMidOneTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.classList.toggle('text-muted', !completedMidOneTotals.length);
        }

        function updateEvaluationOneMid2Average() {
            const averageInput = document.getElementById('evaluationOneMid2Average');
            const averageNote = document.getElementById('evaluationOneMid2AverageNote');
            const evaluationOneMarksBody = marksBodyMap['1'];
            if (!averageInput || !averageNote || !evaluationOneMarksBody) return;

            const completedMidTwoTotals = Array.from(evaluationOneMarksBody.querySelectorAll('tr'))
                .map(function (row) { return row.querySelector('.mid2-total').textContent.trim(); })
                .filter(function (total) { return total !== '-' && total !== ''; })
                .map(parseScore);
            const averageAchieved = completedMidTwoTotals.length
                ? completedMidTwoTotals.reduce(function (sum, total) { return sum + total; }, 0)
                    / (completedMidTwoTotals.length * 30) * 100
                : 0;
            const isAtOrAboveLimit = averageAchieved >= 75;

            averageInput.value = averageAchieved.toFixed(1) + '%';
            averageInput.classList.toggle('is-invalid', isAtOrAboveLimit);
            averageInput.classList.toggle('is-valid', completedMidTwoTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.textContent = !completedMidTwoTotals.length
                ? 'No MID-2 totals entered yet'
                : (isAtOrAboveLimit
                    ? 'At or above 75% â€” reduce MID-2 marks'
                    : 'Below 75% â€” requirement met');
            averageNote.classList.toggle('text-danger', isAtOrAboveLimit);
            averageNote.classList.toggle('text-success', completedMidTwoTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.classList.toggle('text-muted', !completedMidTwoTotals.length);
        }

        function updateEvaluationOneTotalAverage() {
            const averageInput = document.getElementById('evaluationOneTotalAverage');
            const averageNote = document.getElementById('evaluationOneTotalAverageNote');
            const evaluationOneMarksBody = marksBodyMap['1'];
            if (!averageInput || !averageNote || !evaluationOneMarksBody) return;

            const completedTotals = Array.from(evaluationOneMarksBody.querySelectorAll('tr'))
                .map(function (row) { return row.querySelector('.total').textContent.trim(); })
                .filter(function (total) { return total !== '-' && total !== ''; })
                .map(parseScore);
            const averageAchieved = completedTotals.length
                ? completedTotals.reduce(function (sum, total) { return sum + total; }, 0)
                    / (completedTotals.length * 40) * 100
                : 0;
            const isBelowTarget = averageAchieved < 75;

            averageInput.value = averageAchieved.toFixed(1) + '%';
            averageInput.classList.toggle('is-invalid', completedTotals.length > 0 && isBelowTarget);
            averageInput.classList.toggle('is-valid', completedTotals.length > 0 && !isBelowTarget);
            averageNote.textContent = !completedTotals.length
                ? 'No Total (40) values entered yet'
                : (isBelowTarget
                    ? 'Below 75% — increase total marks'
                    : 'At or above 75% — requirement met');
            averageNote.classList.toggle('text-danger', completedTotals.length > 0 && isBelowTarget);
            averageNote.classList.toggle('text-success', completedTotals.length > 0 && !isBelowTarget);
            averageNote.classList.toggle('text-muted', !completedTotals.length);
        }

        function updateEvaluationTwoMid1Average() {
            const averageInput = document.getElementById('evaluationTwoMid1Average');
            const averageNote = document.getElementById('evaluationTwoMid1AverageNote');
            const evaluationTwoMarksBody = marksBodyMap['2'];
            if (!averageInput || !averageNote || !evaluationTwoMarksBody) return;

            const completedMidOneTotals = Array.from(evaluationTwoMarksBody.querySelectorAll('tr'))
                .map(function (row) { return row.querySelector('.mid1-total').textContent.trim(); })
                .filter(function (total) { return total !== '-' && total !== ''; })
                .map(parseScore);
            const averageAchieved = completedMidOneTotals.length
                ? completedMidOneTotals.reduce(function (sum, total) { return sum + total; }, 0)
                    / (completedMidOneTotals.length * 30) * 100
                : 0;
            const isAtOrAboveLimit = averageAchieved >= 75;

            averageInput.value = averageAchieved.toFixed(1) + '%';
            averageInput.classList.toggle('is-invalid', isAtOrAboveLimit);
            averageInput.classList.toggle('is-valid', completedMidOneTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.textContent = !completedMidOneTotals.length
                ? 'No MID-1 totals entered yet'
                : (isAtOrAboveLimit
                    ? 'At or above 75% — reduce MID-1 marks'
                    : 'Below 75% — requirement met');
            averageNote.classList.toggle('text-danger', isAtOrAboveLimit);
            averageNote.classList.toggle('text-success', completedMidOneTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.classList.toggle('text-muted', !completedMidOneTotals.length);
        }

        function updateEvaluationTwoMid2Average() {
            const averageInput = document.getElementById('evaluationTwoMid2Average');
            const averageNote = document.getElementById('evaluationTwoMid2AverageNote');
            const evaluationTwoMarksBody = marksBodyMap['2'];
            if (!averageInput || !averageNote || !evaluationTwoMarksBody) return;

            const completedMidTwoTotals = Array.from(evaluationTwoMarksBody.querySelectorAll('tr'))
                .map(function (row) { return row.querySelector('.mid2-total').textContent.trim(); })
                .filter(function (total) { return total !== '-' && total !== ''; })
                .map(parseScore);
            const averageAchieved = completedMidTwoTotals.length
                ? completedMidTwoTotals.reduce(function (sum, total) { return sum + total; }, 0)
                    / (completedMidTwoTotals.length * 30) * 100
                : 0;
            const isAtOrAboveLimit = averageAchieved >= 75;

            averageInput.value = averageAchieved.toFixed(1) + '%';
            averageInput.classList.toggle('is-invalid', isAtOrAboveLimit);
            averageInput.classList.toggle('is-valid', completedMidTwoTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.textContent = !completedMidTwoTotals.length
                ? 'No MID-2 totals entered yet'
                : (isAtOrAboveLimit
                    ? 'At or above 75% — reduce MID-2 marks'
                    : 'Below 75% — requirement met');
            averageNote.classList.toggle('text-danger', isAtOrAboveLimit);
            averageNote.classList.toggle('text-success', completedMidTwoTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.classList.toggle('text-muted', !completedMidTwoTotals.length);
        }

        function updateEvaluationTwoTotalAverage() {
            const averageInput = document.getElementById('evaluationTwoTotalAverage');
            const averageNote = document.getElementById('evaluationTwoTotalAverageNote');
            const evaluationTwoMarksBody = marksBodyMap['2'];
            if (!averageInput || !averageNote || !evaluationTwoMarksBody) return;

            const completedTotals = Array.from(evaluationTwoMarksBody.querySelectorAll('tr'))
                .map(function (row) { return row.querySelector('.total').textContent.trim(); })
                .filter(function (total) { return total !== '-' && total !== ''; })
                .map(parseScore);
            const averageAchieved = completedTotals.length
                ? completedTotals.reduce(function (sum, total) { return sum + total; }, 0)
                    / (completedTotals.length * 40) * 100
                : 0;
            const isBelowTarget = averageAchieved < 75;

            averageInput.value = averageAchieved.toFixed(1) + '%';
            averageInput.classList.toggle('is-invalid', completedTotals.length > 0 && isBelowTarget);
            averageInput.classList.toggle('is-valid', completedTotals.length > 0 && !isBelowTarget);
            averageNote.textContent = !completedTotals.length
                ? 'No Total (40) values entered yet'
                : (isBelowTarget
                    ? 'Below 75% — increase total marks'
                    : 'At or above 75% — requirement met');
            averageNote.classList.toggle('text-danger', completedTotals.length > 0 && isBelowTarget);
            averageNote.classList.toggle('text-success', completedTotals.length > 0 && !isBelowTarget);
            averageNote.classList.toggle('text-muted', !completedTotals.length);
        }

        function updateEvaluationThreeMid1Average() {
            const averageInput = document.getElementById('evaluationThreeMid1Average');
            const averageNote = document.getElementById('evaluationThreeMid1AverageNote');
            const evaluationThreeMarksBody = marksBodyMap['3'];
            if (!averageInput || !averageNote || !evaluationThreeMarksBody) return;

            const completedMidOneTotals = Array.from(evaluationThreeMarksBody.querySelectorAll('tr'))
                .filter(function (row) {
                    return Array.from(row.querySelectorAll('.mid1-cia, .mid1-viva, .mid1-exam'))
                        .some(function (input) { return input.value.trim() !== ''; });
                })
                .map(function (row) { return row.querySelector('.mid1-total').textContent.trim(); })
                .filter(function (total) { return total !== '-' && total !== ''; })
                .map(parseScore);
            const averageAchieved = completedMidOneTotals.length
                ? completedMidOneTotals.reduce(function (sum, total) { return sum + total; }, 0)
                    / (completedMidOneTotals.length * 30) * 100
                : 0;
            const isAtOrAboveLimit = averageAchieved >= 75;

            averageInput.value = averageAchieved.toFixed(1) + '%';
            averageInput.classList.toggle('is-invalid', isAtOrAboveLimit);
            averageInput.classList.toggle('is-valid', completedMidOneTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.textContent = !completedMidOneTotals.length
                ? 'No MID-1 totals entered yet'
                : (isAtOrAboveLimit
                    ? 'At or above 75% — reduce MID-1 marks'
                    : 'Below 75% — requirement met');
            averageNote.classList.toggle('text-danger', isAtOrAboveLimit);
            averageNote.classList.toggle('text-success', completedMidOneTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.classList.toggle('text-muted', !completedMidOneTotals.length);
        }

        function updateEvaluationThreeMid2Average() {
            const averageInput = document.getElementById('evaluationThreeMid2Average');
            const averageNote = document.getElementById('evaluationThreeMid2AverageNote');
            const evaluationThreeMarksBody = marksBodyMap['3'];
            if (!averageInput || !averageNote || !evaluationThreeMarksBody) return;

            const completedMidTwoTotals = Array.from(evaluationThreeMarksBody.querySelectorAll('tr'))
                .filter(function (row) {
                    return Array.from(row.querySelectorAll('.mid2-cia, .mid2-viva, .mid2-exam'))
                        .some(function (input) { return input.value.trim() !== ''; });
                })
                .map(function (row) { return row.querySelector('.mid2-total').textContent.trim(); })
                .filter(function (total) { return total !== '-' && total !== ''; })
                .map(parseScore);
            const averageAchieved = completedMidTwoTotals.length
                ? completedMidTwoTotals.reduce(function (sum, total) { return sum + total; }, 0)
                    / (completedMidTwoTotals.length * 30) * 100
                : 0;
            const isAtOrAboveLimit = averageAchieved >= 75;

            averageInput.value = averageAchieved.toFixed(1) + '%';
            averageInput.classList.toggle('is-invalid', isAtOrAboveLimit);
            averageInput.classList.toggle('is-valid', completedMidTwoTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.textContent = !completedMidTwoTotals.length
                ? 'No MID-2 totals entered yet'
                : (isAtOrAboveLimit
                    ? 'At or above 75% — reduce MID-2 marks'
                    : 'Below 75% — requirement met');
            averageNote.classList.toggle('text-danger', isAtOrAboveLimit);
            averageNote.classList.toggle('text-success', completedMidTwoTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.classList.toggle('text-muted', !completedMidTwoTotals.length);
        }

        function updateEvaluationThreeTotalAverage() {
            const averageInput = document.getElementById('evaluationThreeTotalAverage');
            const averageNote = document.getElementById('evaluationThreeTotalAverageNote');
            const evaluationThreeMarksBody = marksBodyMap['3'];
            if (!averageInput || !averageNote || !evaluationThreeMarksBody) return;

            const completedTotals = Array.from(evaluationThreeMarksBody.querySelectorAll('tr'))
                .filter(function (row) {
                    return row.querySelector('.grade').textContent.trim() !== '-';
                })
                .map(function (row) { return row.querySelector('.total').textContent.trim(); })
                .filter(function (total) { return total !== '-' && total !== ''; })
                .map(parseScore);
            const averageAchieved = completedTotals.length
                ? completedTotals.reduce(function (sum, total) { return sum + total; }, 0)
                    / (completedTotals.length * 40) * 100
                : 0;
            const isBelowTarget = averageAchieved < 75;

            averageInput.value = averageAchieved.toFixed(1) + '%';
            averageInput.classList.toggle('is-invalid', completedTotals.length > 0 && isBelowTarget);
            averageInput.classList.toggle('is-valid', completedTotals.length > 0 && !isBelowTarget);
            averageNote.textContent = !completedTotals.length
                ? 'No Total (40) values entered yet'
                : (isBelowTarget
                    ? 'Below 75% — increase total marks'
                    : 'At or above 75% — requirement met');
            averageNote.classList.toggle('text-danger', completedTotals.length > 0 && isBelowTarget);
            averageNote.classList.toggle('text-success', completedTotals.length > 0 && !isBelowTarget);
            averageNote.classList.toggle('text-muted', !completedTotals.length);
        }

        function updateEvaluationFourMid1Average() {
            const averageInput = document.getElementById('evaluationFourMid1Average');
            const averageNote = document.getElementById('evaluationFourMid1AverageNote');
            const evaluationFourMarksBody = marksBodyMap['4'];
            if (!averageInput || !averageNote || !evaluationFourMarksBody) return;

            const completedMidOneTotals = Array.from(evaluationFourMarksBody.querySelectorAll('tr'))
                .map(function (row) { return row.querySelector('.mid1-total').textContent.trim(); })
                .filter(function (total) { return total !== '-' && total !== ''; })
                .map(parseScore);
            const averageAchieved = completedMidOneTotals.length
                ? completedMidOneTotals.reduce(function (sum, total) { return sum + total; }, 0)
                    / (completedMidOneTotals.length * 30) * 100
                : 0;
            const isAtOrAboveLimit = averageAchieved >= 75;

            averageInput.value = averageAchieved.toFixed(1) + '%';
            averageInput.classList.toggle('is-invalid', isAtOrAboveLimit);
            averageInput.classList.toggle('is-valid', completedMidOneTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.textContent = !completedMidOneTotals.length
                ? 'No MID-1 totals entered yet'
                : (isAtOrAboveLimit
                    ? 'At or above 75% — reduce MID-1 marks'
                    : 'Below 75% — requirement met');
            averageNote.classList.toggle('text-danger', isAtOrAboveLimit);
            averageNote.classList.toggle('text-success', completedMidOneTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.classList.toggle('text-muted', !completedMidOneTotals.length);
        }

        function updateEvaluationFourMid2Average() {
            const averageInput = document.getElementById('evaluationFourMid2Average');
            const averageNote = document.getElementById('evaluationFourMid2AverageNote');
            const evaluationFourMarksBody = marksBodyMap['4'];
            if (!averageInput || !averageNote || !evaluationFourMarksBody) return;

            const completedMidTwoTotals = Array.from(evaluationFourMarksBody.querySelectorAll('tr'))
                .map(function (row) { return row.querySelector('.mid2-total').textContent.trim(); })
                .filter(function (total) { return total !== '-' && total !== ''; })
                .map(parseScore);
            const averageAchieved = completedMidTwoTotals.length
                ? completedMidTwoTotals.reduce(function (sum, total) { return sum + total; }, 0)
                    / (completedMidTwoTotals.length * 30) * 100
                : 0;
            const isAtOrAboveLimit = averageAchieved >= 75;

            averageInput.value = averageAchieved.toFixed(1) + '%';
            averageInput.classList.toggle('is-invalid', isAtOrAboveLimit);
            averageInput.classList.toggle('is-valid', completedMidTwoTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.textContent = !completedMidTwoTotals.length
                ? 'No MID-2 totals entered yet'
                : (isAtOrAboveLimit
                    ? 'At or above 75% — reduce MID-2 marks'
                    : 'Below 75% — requirement met');
            averageNote.classList.toggle('text-danger', isAtOrAboveLimit);
            averageNote.classList.toggle('text-success', completedMidTwoTotals.length > 0 && !isAtOrAboveLimit);
            averageNote.classList.toggle('text-muted', !completedMidTwoTotals.length);
        }

        function updateEvaluationFourTotalAverage() {
            const averageInput = document.getElementById('evaluationFourTotalAverage');
            const averageNote = document.getElementById('evaluationFourTotalAverageNote');
            const evaluationFourMarksBody = marksBodyMap['4'];
            if (!averageInput || !averageNote || !evaluationFourMarksBody) return;

            const completedTotals = Array.from(evaluationFourMarksBody.querySelectorAll('tr'))
                .map(function (row) { return row.querySelector('.total').textContent.trim(); })
                .filter(function (total) { return total !== '-' && total !== ''; })
                .map(parseScore);
            const averageAchieved = completedTotals.length
                ? completedTotals.reduce(function (sum, total) { return sum + total; }, 0)
                    / (completedTotals.length * 40) * 100
                : 0;
            const isBelowTarget = averageAchieved < 75;

            averageInput.value = averageAchieved.toFixed(1) + '%';
            averageInput.classList.toggle('is-invalid', completedTotals.length > 0 && isBelowTarget);
            averageInput.classList.toggle('is-valid', completedTotals.length > 0 && !isBelowTarget);
            averageNote.textContent = !completedTotals.length
                ? 'No Total (40) values entered yet'
                : (isBelowTarget
                    ? 'Below 75% — increase total marks'
                    : 'At or above 75% — requirement met');
            averageNote.classList.toggle('text-danger', completedTotals.length > 0 && isBelowTarget);
            averageNote.classList.toggle('text-success', completedTotals.length > 0 && !isBelowTarget);
            averageNote.classList.toggle('text-muted', !completedTotals.length);
        }

        function updateAllEvaluationAverages() {
            updateEvaluationOneMid1Average();
            updateEvaluationOneMid2Average();
            updateEvaluationOneTotalAverage();
            updateEvaluationTwoMid1Average();
            updateEvaluationTwoMid2Average();
            updateEvaluationTwoTotalAverage();
            updateEvaluationThreeMid1Average();
            updateEvaluationThreeMid2Average();
            updateEvaluationThreeTotalAverage();
            updateEvaluationFourMid1Average();
            updateEvaluationFourMid2Average();
            updateEvaluationFourTotalAverage();
        }

        function renderAttendanceGradeSummary(students, tbody) {
            const grades = calculateDistributedAttendanceGrades(students);
            const totalGraded = Object.keys(grades).reduce(function (total, grade) {
                return total + grades[grade].students.length;
            }, 0);
            const gradeRows = [
                { grade: 'O', label: 'O (>=90%)', expected: '10 - 15%', limit: '17%' },
                { grade: 'A+', label: 'A+ (80-89%)', expected: '20 - 25%', limit: '28%' },
                { grade: 'A', label: 'A (70-79%)', expected: '20 - 25%', limit: '28%' },
                { grade: 'B+', label: 'B+ (60-69%)', expected: '20 - 25%', limit: '28%' },
                { grade: 'B', label: 'B (50-59%)', expected: '10 - 15%', limit: '17%', lowerBandStart: true },
                { grade: 'P', label: 'P (40-49%)', lowerBandMember: true },
                { grade: 'F', label: 'F (<40%)', lowerBandMember: true }
            ];

            tbody.innerHTML = '';

            gradeRows.forEach(function (gradeRow) {
                const grade = gradeRow.grade;
                const selectedStudents = grades[grade].students;
                const count = selectedStudents.length;
                const percentage = grades[grade].allocatedPercentage.toFixed(1);
                const selectedStudentLabels = selectedStudents.map(function (student) {
                    return escapeHtml((student.rollNo || 'Student ' + (student.originalIndex + 1)).trim())
                        + ' (' + student.attendancePercentage.toFixed(1) + '%)';
                }).join(', ');
                const row = document.createElement('tr');
                let distributionCells = '';
                if (gradeRow.lowerBandStart) {
                    distributionCells = '<td rowspan="3" class="align-middle">' + gradeRow.expected + '</td>'
                        + '<td rowspan="3" class="align-middle">' + gradeRow.limit + '</td>';
                } else if (!gradeRow.lowerBandMember) {
                    distributionCells = '<td>' + gradeRow.expected + '</td><td>' + gradeRow.limit + '</td>';
                }
                row.innerHTML = '<td><strong>' + gradeRow.label + '</strong></td>'
                    + distributionCells
                    + '<td><strong>' + percentage + '%</strong></td>'
                    + '<td><strong>' + count + '</strong>'
                    + '<div class="small text-muted mt-1" style="white-space: normal; min-width: 180px;">'
                    + (selectedStudentLabels || 'No students selected') + '</div></td>';
                tbody.appendChild(row);
            });

            const totalRow = document.createElement('tr');
            totalRow.innerHTML = ''
                + '<td><strong>Total</strong></td>'
                + '<td><strong>100%</strong></td>'
                + '<td><strong>100%</strong></td>'
                + '<td><strong>---</strong></td>'
                + '<td><strong>' + totalGraded + '</strong></td>';
            tbody.appendChild(totalRow);
        }

        function renderMarksGradeSummary(students, tbody) {
            const grades = calculateGradeDistribution(students);
            const gradeOrder = [
                { grade: 'O', range: '37-40' },
                { grade: 'A+', range: '32-36' },
                { grade: 'A', range: '28-31' },
                { grade: 'B+', range: '24-27' },
                { grade: 'B', range: '20-23' },
                { grade: 'P', range: '14-19' },
                { grade: 'F', range: '0-13' }
            ];
            const totalGraded = gradeOrder.reduce(function (total, item) {
                return total + grades[item.grade].count;
            }, 0);

            tbody.innerHTML = '';
            gradeOrder.forEach(function (item) {
                const grade = grades[item.grade];
                const percentage = totalGraded ? (grade.count / totalGraded * 100).toFixed(1) : '0.0';
                const rollNumbers = grade.rolls.map(escapeHtml).join(', ');
                const row = document.createElement('tr');
                row.innerHTML = '<td><strong>' + item.grade + '</strong></td>'
                    + '<td>' + item.range + '</td>'
                    + '<td><strong>' + grade.count + '</strong></td>'
                    + '<td>' + percentage + '%</td>'
                    + '<td>' + (rollNumbers || '—') + '</td>';
                tbody.appendChild(row);
            });

            const totalRow = document.createElement('tr');
            totalRow.innerHTML = '<td><strong>Total graded</strong></td><td>—</td>'
                + '<td><strong>' + totalGraded + '</strong></td>'
                + '<td>' + (totalGraded ? '100.0%' : '0.0%') + '</td><td>—</td>';
            tbody.appendChild(totalRow);
        }

        function updateGradeSummary() {
            const students = getEvaluationRows();
            renderMarksGradeSummary(
                students,
                document.getElementById('gradeSummaryBody' + activeEvaluationSheet)
            );
            renderAttendanceGradeSummary(
                students,
                document.getElementById('attendanceGradeSummaryBody' + activeEvaluationSheet)
            );
        }

        function saveEvaluationSheetData(sheetNumber) {
            const evaluationNumber = sheetNumber || activeEvaluationSheet;
            const previousActiveSheet = activeEvaluationSheet;
            activeEvaluationSheet = evaluationNumber;
            try {
                const subjectNameInput = evaluationSubjectNameMap[evaluationNumber];
                const payload = {
                    studentCount: document.getElementById('studentCount') ? document.getElementById('studentCount').value : '',
                    subjectName: subjectNameInput ? subjectNameInput.value.trim() : '',
                    attendanceVersion: evaluationAttendanceVersion,
                    objectiveMarksVersion: evaluationNumber === '1' ? firstEvaluationObjectiveMarksVersion
                        : (evaluationNumber === '2' ? secondEvaluationObjectiveMarksVersion : 0),
                    assignmentMarksVersion: evaluationNumber === '1' ? firstEvaluationAssignmentMarksVersion : 0,
                    mid2ObjMarksVersion: evaluationNumber === '1' ? firstEvaluationMid2ObjectiveMarksVersion : 0,
                    vivaMarksVersion: evaluationNumber === '1' ? firstEvaluationVivaMarksVersion : 0,
                    projectMarksVersion: evaluationNumber === '4' ? fourthEvaluationProjectMarksVersion : 0,
                    rows: getEvaluationRows(evaluationNumber),
                    savedAt: new Date().toISOString()
                };
                localStorage.setItem(getActiveEvaluationStorageKey(), JSON.stringify(payload));
                setStatus(evaluationSaveStatus, 'Internal Evaluation ' + evaluationNumber
                    + ' saved at ' + formatSavedTime(payload.savedAt), 'success');
            } finally {
                activeEvaluationSheet = previousActiveSheet;
            }
        }

        function saveEvaluationData() {
            saveEvaluationSheetData(activeEvaluationSheet);
        }

        function loadEvaluationData() {
            const saved = localStorage.getItem(getActiveEvaluationStorageKey());
            const activeRollNumbers = getActiveEvaluationRollNumbers();
            const activeAttendance = getActiveEvaluationAttendance();
            const defaultCount = activeRollNumbers.length;

            if (!saved) {
                document.getElementById('studentCount').value = String(defaultCount);
                renderStudents(generateStudents(defaultCount));
                setStatus(evaluationSaveStatus, 'Internal Evaluation ' + activeEvaluationSheet
                    + ' is ready. Save after editing.', 'muted');
                return;
            }

            try {
                const payload = JSON.parse(saved);
                const subjectNameInput = evaluationSubjectNameMap[activeEvaluationSheet];
                if (subjectNameInput && payload.subjectName !== undefined) {
                    subjectNameInput.value = String(payload.subjectName || '');
                }
                let savedRows = Array.isArray(payload.rows) ? payload.rows.map(function (student) {
                    const rollIndex = activeRollNumbers.indexOf(String(student.rollNo || '').trim());
                    if (rollIndex >= 0 && (payload.attendanceVersion !== evaluationAttendanceVersion
                            || student.attendance === undefined || student.attendance === '')) {
                        return Object.assign({}, student, {
                            attendance: activeAttendance[rollIndex] === undefined
                                ? '' : String(activeAttendance[rollIndex])
                        });
                    }
                    return student;
                }) : [];
                if (activeEvaluationSheet === '1') {
                    const savedRowsByRollNumber = {};
                    savedRows.forEach(function (student) {
                        const rollNo = String(student.rollNo || '').trim().toUpperCase();
                        if (rollNo) savedRowsByRollNumber[rollNo] = student;
                    });
                    savedRows = activeRollNumbers.map(function (rollNo, index) {
                        const existing = savedRowsByRollNumber[rollNo.trim().toUpperCase()] || {};
                        const legacyAssignment = existing.assignment !== undefined ? existing.assignment : '';
                        return Object.assign({
                            attendance: String(activeAttendance[index] ?? ''),
                            mid1Obj: '', mid1Desc: '', mid2Obj: '', mid2Desc: '',
                            assignment1: '', assignment2: '', assignment: '', viva: ''
                        }, existing, {
                            rollNo: rollNo,
                            assignment1: existing.assignment1 !== undefined && existing.assignment1 !== '' ? existing.assignment1 : legacyAssignment,
                            assignment2: existing.assignment2 !== undefined && existing.assignment2 !== '' ? existing.assignment2 : legacyAssignment
                        });
                    });
                }
                if (activeEvaluationSheet === '2') {
                    const savedRowsByRollNumber = {};
                    savedRows.forEach(function (student) {
                        const rollNo = String(student.rollNo || '').trim();
                        if (rollNo) savedRowsByRollNumber[rollNo] = student;
                    });
                    savedRows = secondEvaluationRollNumbers.map(function (rollNo, index) {
                        const seededMid1Obj = secondEvaluationObjectiveMarks[index] === undefined
                            ? '' : String(secondEvaluationObjectiveMarks[index]);
                        return Object.assign({
                            mid1Obj: '', mid1Desc: '', mid2Obj: '', mid2Desc: '', assignment: '', viva: ''
                        }, savedRowsByRollNumber[rollNo] || {}, {
                            rollNo: rollNo,
                            attendance: String(secondEvaluationAttendance[index])
                        });
                    });
                    if (payload.objectiveMarksVersion !== secondEvaluationObjectiveMarksVersion) {
                        savedRows = savedRows.map(function (student, index) {
                            const seed = secondEvaluationObjectiveMarks[index];
                            if (student.mid1Obj && String(student.mid1Obj).trim()) return student;
                            return Object.assign({}, student, {
                                mid1Obj: seed === undefined ? '' : String(seed)
                            });
                        });
                    }
                }
                if (activeEvaluationSheet === '1' && payload.objectiveMarksVersion !== firstEvaluationObjectiveMarksVersion) {
                    savedRows = savedRows.map(function (student, index) {
                        const seed = firstEvaluationObjectiveMarks[getEvaluationOneSeedIndex(student, index)];
                        if (student.mid1Obj && String(student.mid1Obj).trim()) return student;
                        return Object.assign({}, student, {
                            mid1Obj: seed === undefined || seed === '' ? '' : String(seed)
                        });
                    });
                }
                if (activeEvaluationSheet === '1' && payload.assignmentMarksVersion !== firstEvaluationAssignmentMarksVersion) {
                    savedRows = savedRows.map(function (student, index) {
                        if ((student.assignment1 && String(student.assignment1).trim()) || (student.assignment2 && String(student.assignment2).trim())) return student;
                        const seed = firstEvaluationAssignmentMarks[getEvaluationOneSeedIndex(student, index)];
                        const seedVal = seed === undefined || seed === '' ? '' : String(seed);
                        return Object.assign({}, student, {
                            assignment1: seedVal,
                            assignment2: seedVal
                        });
                    });
                }
                if (activeEvaluationSheet === '1' && payload.mid2ObjMarksVersion !== firstEvaluationMid2ObjectiveMarksVersion) {
                    savedRows = savedRows.map(function (student, index) {
                        if (student.mid2Obj && String(student.mid2Obj).trim()) return student;
                        const seed = firstEvaluationMid2ObjectiveMarks[getEvaluationOneSeedIndex(student, index)];
                        return Object.assign({}, student, {
                            mid2Obj: seed === undefined || seed === '' ? '' : String(seed)
                        });
                    });
                }
                if (activeEvaluationSheet === '1' && payload.vivaMarksVersion !== firstEvaluationVivaMarksVersion) {
                    savedRows = savedRows.map(function (student, index) {
                        if (student.viva && String(student.viva).trim()) return student;
                        const seed = firstEvaluationVivaMarks[getEvaluationOneSeedIndex(student, index)];
                        return Object.assign({}, student, {
                            viva: seed === undefined || seed === '' ? '' : String(seed)
                        });
                    });
                }
                if (activeEvaluationSheet === '3') {
                    const savedRowsByRollNumber = {};
                    savedRows.forEach(function (student) {
                        const rollNo = String(student.rollNo || '').trim().toUpperCase();
                        if (rollNo) savedRowsByRollNumber[rollNo] = student;
                    });
                    savedRows = activeRollNumbers.map(function (rollNo, index) {
                        const existing = savedRowsByRollNumber[String(rollNo).trim().toUpperCase()] || {};
                        return Object.assign({
                            attendance: activeAttendance[index] === undefined ? '' : String(activeAttendance[index]),
                            mid1Cia: '', mid1Viva: '', mid1Exam: '',
                            mid2Cia: '', mid2Viva: '', mid2Exam: '', project: ''
                        }, existing, {
                            rollNo: rollNo,
                            attendance: activeAttendance[index] === undefined ? '' : String(activeAttendance[index])
                        });
                    });
                }
                if (activeEvaluationSheet === '4') {
                    const savedRowsByRollNumber = {};
                    savedRows.forEach(function (student) {
                        const rollNo = String(student.rollNo || '').trim().toUpperCase();
                        if (rollNo) savedRowsByRollNumber[rollNo] = student;
                    });
                    savedRows = activeRollNumbers.map(function (rollNo, index) {
                        const existing = savedRowsByRollNumber[String(rollNo).trim().toUpperCase()] || {};
                        const seededProject = fourthEvaluationProjectMarks[index] !== undefined ? String(fourthEvaluationProjectMarks[index]) : '';
                        const projectVal = payload.projectMarksVersion === fourthEvaluationProjectMarksVersion
                            ? (existing.project !== undefined && existing.project !== '' ? existing.project : seededProject)
                            : seededProject;
                        return Object.assign({
                            attendance: activeAttendance[index] === undefined ? '' : String(activeAttendance[index]),
                            mid1Cia: '', mid1Viva: '', mid1Exam: '',
                            mid2Cia: '', mid2Viva: '', mid2Exam: '', project: ''
                        }, existing, {
                            rollNo: rollNo,
                            attendance: activeAttendance[index] === undefined ? '' : String(activeAttendance[index]),
                            project: projectVal
                        });
                    });
                }
                const hasEnteredMarks = savedRows.some(function (student) {
                if (activeEvaluationSheet === '3' || activeEvaluationSheet === '4') {
                        return [student.mid1Cia, student.mid1Viva, student.mid1Exam, student.mid2Cia, student.mid2Viva, student.mid2Exam, student.project]
                            .some(function (value) { return String(value || '').trim(); });
                    }
                    return [student.mid1Obj, student.mid1Desc, student.mid2Obj, student.mid2Desc, student.assignment, student.viva]
                        .some(function (value) { return String(value || '').trim(); });
                });
                const hasCustomRollNumbers = savedRows.some(function (student) {
                    const rollNo = String(student.rollNo || '').trim();
                    return rollNo && !/^BT\d{3}$/.test(rollNo);
                });

                if (!hasEnteredMarks && !hasCustomRollNumbers) {
                    document.getElementById('studentCount').value = String(activeRollNumbers.length);
                    renderStudents(generateStudents(activeRollNumbers.length));
                    setStatus(evaluationSaveStatus, 'Evaluation roll numbers loaded. Save after editing.', 'success');
                    return;
                }

                document.getElementById('studentCount').value = activeEvaluationSheet === '3'
                    ? String(defaultCount) : (payload.studentCount || String(defaultCount));
                renderStudents(savedRows.length ? savedRows : generateStudents(defaultCount));
                setStatus(evaluationSaveStatus, 'Evaluation loaded from ' + formatSavedTime(payload.savedAt), 'success');
            } catch (error) {
                console.error('Failed to load evaluation data', error);
                renderStudents(generateStudents(defaultCount));
                setStatus(evaluationSaveStatus, 'Could not read saved evaluation', 'warning');
            }
        }

        function clearEvaluationData() {
            if (!confirm('Clear the saved evaluation and reset the marks sheet?')) {
                return;
            }

            localStorage.removeItem(getActiveEvaluationStorageKey());
            const count = getActiveEvaluationRollNumbers().length;
            document.getElementById('studentCount').value = String(count);
            renderStudents(generateStudents(count));
            setStatus(evaluationSaveStatus, 'Internal Evaluation ' + activeEvaluationSheet + ' cleared', 'muted');
        }

        function createAdditionalEvaluationSheet(count, requestedSheetNumber) {
            const existingNumbers = Object.keys(marksBodyMap).map(function (value) { return parseInt(value, 10); });
            const sheetNumber = String(requestedSheetNumber || (Math.max.apply(null, existingNumbers) + 1));
            if (marksBodyMap[sheetNumber]) return sheetNumber;

            const sourceSection = evaluationSectionsMap['3'];
            const section = sourceSection.cloneNode(true);
            section.querySelectorAll('.evaluation-horizontal-scroll').forEach(function (scrollbar) {
                scrollbar.remove();
            });
            section.dataset.sheet = sheetNumber;
            section.style.display = 'block';
            section.classList.add('mt-5');
            section.querySelector('h5').innerHTML = '<i class="fas fa-graduation-cap me-2"></i>Internal Evaluation ' + sheetNumber;
            section.querySelector('.small.text-muted').textContent = 'A new independent internal evaluation sheet for '
                + count + ' students. Existing evaluation sheets and marks are preserved.';
            section.querySelector('.marks-grade-summary .card-title').textContent =
                'Grade Distribution Summary - Evaluation ' + sheetNumber;
            section.querySelector('.attendance-grade-summary .card-title').textContent =
                'Attendance Grade Distribution Summary - Evaluation ' + sheetNumber;
            section.querySelectorAll('[id]').forEach(function (element) {
                element.id = element.id.replace(/3$/, sheetNumber);
            });
            section.querySelector('tbody[id^="marksBody"]').innerHTML = '';
            section.querySelector('tbody[id^="gradeSummaryBody"]').innerHTML = '';
            sourceSection.parentNode.appendChild(section);

            marksBodyMap[sheetNumber] = document.getElementById('marksBody' + sheetNumber);
            evaluationSectionsMap[sheetNumber] = section;
            gradeSummaryTableMap[sheetNumber] = document.getElementById('gradeSummaryTable' + sheetNumber);
            evaluationStorageKeys[sheetNumber] = 'examBranchEvaluationDataSheet' + sheetNumber;

            const option = document.createElement('option');
            option.value = sheetNumber;
            option.textContent = 'Internal Evaluation ' + sheetNumber;
            evaluationSheetSelect.appendChild(option);

            marksBodyMap[sheetNumber].addEventListener('input', function (event) {
                if (!event.target.closest('tr')) return;
                activeEvaluationSheet = sheetNumber;
                evaluationSheetSelect.value = sheetNumber;
                recalculateEvaluationRow(event.target.closest('tr'));
                updateAttendanceGrades();
                updateGradeSummary();
                updateEvaluationMetrics();
                updateAllEvaluationAverages();
                markEvaluationDirty();
            });
            return sheetNumber;
        }

        function regenerateStudentSheet() {
            const count = Math.max(1, parseInt(document.getElementById('studentCount').value, 10) || 50);
            const sheetNumber = createAdditionalEvaluationSheet(count);
            const savedDynamicSheets = JSON.parse(localStorage.getItem('examBranchDynamicEvaluationSheets') || '[]');
            savedDynamicSheets.push({ sheetNumber: sheetNumber, count: count });
            localStorage.setItem('examBranchDynamicEvaluationSheets', JSON.stringify(savedDynamicSheets));

            activeEvaluationSheet = sheetNumber;
            evaluationSheetSelect.value = sheetNumber;
            renderStudents(generateStudents(count));
            markEvaluationDirty();
            saveEvaluationData();
            evaluationSectionsMap[sheetNumber].scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        function getTimeTablePayload() {
            const savedSelections = getStoredSubjectSelections();
            const classContexts = getClassTimeTableContexts(savedSelections);
            normalizeAllTimeTableSlotValues();
            const meta = {};
            timeTableMetaFields.forEach(function (field) {
                meta[field.id] = field.value;
            });

            const slots = timeTableSlots.map(function (slot) {
                return {
                    day: slot.dataset.day || '',
                    period: slot.dataset.period || '',
                    value: normalizeTimeTableDisplayValue(slot.value)
                };
            });

            const individualTables = getIndividualTimeTableCards().map(function (card) {
                const individualMeta = {};
                getIndividualTimeTableMetaFields(card).forEach(function (field, index) {
                    const key = field.id || field.getAttribute('aria-label') || 'field' + index;
                    individualMeta[key] = field.value;
                });

                const individualSlots = getIndividualTimeTableSlots(card).map(function (slot) {
                    return {
                        day: slot.dataset.day || '',
                        period: slot.dataset.period || '',
                        value: normalizeTimeTableDisplayValue(slot.value)
                    };
                });

                return {
                    meta: individualMeta,
                    slots: individualSlots
                };
            });

            const emptyTables = emptyTimeTableCards.map(function (card) {
                const emptySlots = getEmptyTimeTableSlots(card).map(function (slot) {
                    return {
                        yearSem: slot.dataset.yearSem || card.dataset.yearSem || '',
                        branch: slot.dataset.branch || card.dataset.branch || '',
                        section: slot.dataset.section || card.dataset.section || '',
                        day: slot.dataset.day || '',
                        period: slot.dataset.period || '',
                        value: normalizeTimeTableDisplayValue(slot.value)
                    };
                });

                return {
                    yearSem: card.dataset.yearSem || '',
                    branch: card.dataset.branch || '',
                    section: card.dataset.section || '',
                    slots: emptySlots
                };
            });

            return {
                meta: meta,
                slots: slots,
                emptyTables: emptyTables,
                individualTables: individualTables,
                individualMeta: individualTables[0] ? individualTables[0].meta : {},
                individualSlots: individualTables[0] ? individualTables[0].slots : [],
                savedAt: new Date().toISOString()
            };
        }

        function setTimeTablePayload(payload) {
            resetClassTimeTableMerges();
            const data = payload || {};
            let repairedSameHourRepeats = 0;
            const meta = data.meta || {};
            timeTableMetaFields.forEach(function (field) {
                if (Object.prototype.hasOwnProperty.call(meta, field.id)) {
                    field.value = meta[field.id] || '';
                }
            });

            const slots = Array.isArray(data.slots) ? data.slots : [];
            timeTableSlots.forEach(function (slot) {
                const match = slots.find(function (entry) {
                    return entry.day === slot.dataset.day && entry.period === slot.dataset.period;
                });
                slot.value = match ? normalizeTimeTableDisplayValue(match.value) : '';
            });
            restoreClassLabMergesFromValues(timeTableSlots);

            if (Object.prototype.hasOwnProperty.call(data, 'emptyTables')) {
                const emptyTables = Array.isArray(data.emptyTables) ? data.emptyTables : [];
                emptyTimeTableCards.forEach(function (card) {
                    const cardSlots = getEmptyTimeTableSlots(card);
                    const tableData = emptyTables.find(function (entry) {
                        return entry.yearSem === card.dataset.yearSem &&
                            entry.branch === card.dataset.branch &&
                            (entry.section || '') === (card.dataset.section || '');
                    }) || {};
                    const emptySlots = Array.isArray(tableData.slots) ? tableData.slots : [];

                    resetClassTimeTableMerges(cardSlots);
                    cardSlots.forEach(function (slot) {
                        const match = emptySlots.find(function (entry) {
                            return entry.day === slot.dataset.day && entry.period === slot.dataset.period;
                        });
                        slot.value = match ? normalizeTimeTableDisplayValue(match.value) : '';
                    });
                    restoreClassLabMergesFromValues(cardSlots);
                });
            }
             const savedSelections = getStoredSubjectSelections();
             const classContexts = getClassTimeTableContexts(savedSelections);
             repairedSameHourRepeats = applyTimeTableRequirementRepairs(classContexts, savedSelections).total;
             repairedSameHourRepeats += repairAllClassLabRoomConflicts(classContexts, savedSelections);
             repairedSameHourRepeats += repairMorningTheoryCoverage(classContexts, savedSelections);

            const individualTables = Array.isArray(data.individualTables) && data.individualTables.length
                ? data.individualTables
                : [];

            const storedClassSelections = getSelectionsForClassContexts(savedSelections, classContexts);
            const storedFacultySchedules = buildIndividualFacultySchedules(storedClassSelections);
            if (storedFacultySchedules.length) {
                renderIndividualFacultyTimeTables(storedClassSelections, classContexts);
                normalizeAllTimeTableSlotValues();
                return repairedSameHourRepeats;
            }

            ensureIndividualTimeTableCardCount(individualTables.length).forEach(function (card, cardIndex) {
                const tableData = individualTables[cardIndex] || {};
                const individualMeta = tableData.meta || {};
                getIndividualTimeTableMetaFields(card).forEach(function (field, index) {
                    const key = field.id || field.getAttribute('aria-label') || 'field' + index;
                    if (Object.prototype.hasOwnProperty.call(individualMeta, key)) {
                        field.value = individualMeta[key] || '';
                    } else {
                        field.value = '';
                    }
                });

                const individualSlots = Array.isArray(tableData.slots) ? tableData.slots : [];
                getIndividualTimeTableSlots(card).forEach(function (slot) {
                    const match = individualSlots.find(function (entry) {
                        return entry.day === slot.dataset.day && entry.period === slot.dataset.period;
                    });
                    slot.value = match ? normalizeTimeTableDisplayValue(match.value) : '';
                });
                restoreIndividualLabMergesFromValues(card);
            });
            normalizeAllTimeTableSlotValues();
            return repairedSameHourRepeats;
        }

        function hasTimeTableContent() {
            return timeTableSlots.some(function (slot) {
                return slot.value.trim();
            }) || getIndividualTimeTableSlots().some(function (slot) {
                return slot.value.trim();
            }) || getIndividualTimeTableMetaFields().some(function (field) {
                return field.value.trim();
            });
        }

        function saveTimeTableData() {
            const payload = getTimeTablePayload();
            localStorage.setItem(timeTableStorageKey, JSON.stringify(payload));
            setStatus(timeTableStatus, 'Timetable saved at ' + formatSavedTime(payload.savedAt), 'success');
        }

        function persistManualTimeTableEdit() {
            const selections = getStoredSubjectSelections();
            const classContexts = getClassTimeTableContexts(selections);
            refreshIndividualTimeTablesFromCurrentSelections();
            saveTimeTableData();
        }

        function loadTimeTableData() {
            const legacySaved = legacyTimeTableStorageKeys.slice().reverse().map(function (key) {
                return localStorage.getItem(key);
            }).find(Boolean);
            let saved = localStorage.getItem(timeTableStorageKey);
            const migratedLegacyTimetable = !saved && Boolean(legacySaved);
            if (migratedLegacyTimetable) {
                saved = legacySaved;
            }
            legacyTimeTableStorageKeys.forEach(function (key) {
                localStorage.removeItem(key);
            });
            if (!saved) {
                const defaultContexts = getClassTimeTableContexts(getStoredSubjectSelections());
                enforceActivitiesLastHours(defaultContexts);
                saveTimeTableData();
                renderAllTimeTableLoadSummaries();
                setStatus(timeTableStatus, 'Blank timetable ready', 'muted');
                return;
            }

            try {
                const payload = JSON.parse(saved);
                const repairedSameHourRepeats = setTimeTablePayload(payload);
                setStatus(
                    timeTableStatus,
                    'Timetable loaded from ' + formatSavedTime(payload.savedAt) +
                    (repairedSameHourRepeats || migratedLegacyTimetable ? '; timetable clashes were corrected' : ''),
                    'success'
                );
                const activityRepairs = enforceActivitiesLastHours(getClassTimeTableContexts(getStoredSubjectSelections()));
                if (repairedSameHourRepeats || migratedLegacyTimetable || activityRepairs) {
                    syncIndividualTimeTablesWithMainTables(getStoredSubjectSelections(), getClassTimeTableContexts(getStoredSubjectSelections()));
                }
                if (repairedSameHourRepeats || migratedLegacyTimetable || activityRepairs) {
                    saveTimeTableData();
                }
            } catch (error) {
                console.error('Failed to load timetable data', error);
                setStatus(timeTableStatus, 'Could not read saved timetable', 'warning');
            }
        }

        function escapeExcelCell(value) {
            return String(value || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        }

        function getCellExportValue(cell) {
            const input = cell.querySelector('textarea, input, select');
            if (input) {
                return input.value || '';
            }
            return cell.textContent || '';
        }

        function buildTableExcelHtml(table, title) {
            let html = '<table border="1">';
            html += '<tr><th colspan="8">' + escapeExcelCell(title || 'Time Table') + '</th></tr>';
            Array.from(table.rows).forEach(function (row) {
                html += '<tr>';
                Array.from(row.cells).forEach(function (cell) {
                    if (cell.style.display === 'none') {
                        return;
                    }
                    const tagName = cell.tagName && cell.tagName.toLowerCase() === 'th' ? 'th' : 'td';
                    const colspan = cell.colSpan && cell.colSpan > 1 ? ' colspan="' + cell.colSpan + '"' : '';
                    const rowspan = cell.rowSpan && cell.rowSpan > 1 ? ' rowspan="' + cell.rowSpan + '"' : '';
                    html += '<' + tagName + colspan + rowspan + '>' + escapeExcelCell(getCellExportValue(cell).trim()) + '</' + tagName + '>';
                });
                html += '</tr>';
            });
            html += '</table>';
            return '<html><head><meta charset="utf-8"></head><body>' + html + '</body></html>';
        }

        async function downloadEvaluationExcel(sheetNumber) {
            const subjectName = evaluationSubjectNameMap[sheetNumber]
                ? evaluationSubjectNameMap[sheetNumber].value.trim() : '';
            const payload = {
                sheetNumber: sheetNumber,
                subjectName: subjectName,
                students: getEvaluationRows(sheetNumber)
            };
            const downloadButton = document.getElementById('evaluationConfirmDownloadBtn');
            downloadButton.disabled = true;
            setStatus(evaluationSaveStatus, 'Preparing Internal Evaluation ' + sheetNumber + ' workbook...', 'muted');
            try {
                const response = await fetch(evaluationWorkbookDownloadUrl, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfTokenValue
                    },
                    body: JSON.stringify(payload)
                });
                if (!response.ok) {
                    const responseType = response.headers.get('Content-Type') || '';
                    const errorBody = responseType.includes('application/json')
                        ? await response.json() : null;
                    throw new Error(errorBody && errorBody.error
                        ? errorBody.error : 'Workbook generation failed (' + response.status + ').');
                }
                const responseType = response.headers.get('Content-Type') || '';
                if (!responseType.includes(
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )) {
                    throw new Error('The server returned an unexpected workbook response.');
                }

                const blob = await response.blob();
                const link = document.createElement('a');
                const downloadUrl = URL.createObjectURL(blob);
                link.href = downloadUrl;
                link.download = 'internal-evaluation-' + sheetNumber + '.xlsx';
                document.body.appendChild(link);
                link.click();
                link.remove();
                window.setTimeout(function () { URL.revokeObjectURL(downloadUrl); }, 1000);
                window.bootstrap.Modal.getOrCreateInstance(
                    document.getElementById('evaluationDownloadModal')
                ).hide();
                setStatus(evaluationSaveStatus, 'Internal Evaluation ' + sheetNumber + ' workbook downloaded', 'success');
            } catch (error) {
                console.error('Failed to download evaluation workbook', error);
                setStatus(evaluationSaveStatus, error.message || 'Could not download evaluation workbook', 'warning');
            } finally {
                downloadButton.disabled = false;
            }
        }

        function downloadMainTimeTableExcel(button) {
            const tableTitle = button.getAttribute('data-table-title') || 'Time Table';
            const tableSelector = button.getAttribute('data-table-selector');
            const table = tableSelector
                ? document.querySelector(tableSelector)
                : button.closest('[data-empty-timetable-card]')?.querySelector('table.time-table-grid');
            if (!table || !table.matches('table.time-table-grid')) {
                setStatus(timeTableStatus, 'Time table not found for download', 'warning');
                return;
            }
            const rows = [];
            const tableHeader = table.tHead && table.tHead.rows.length ? table.tHead.rows[0] : null;
            if (tableHeader) {
                rows.push(Array.from(tableHeader.cells).map(function (cell) {
                    return (cell.textContent || '').trim();
                }));
            }
            const periodColumns = [1, 2, 3, 5, 6, 7];
            Array.from(table.tBodies).forEach(function (body) {
                Array.from(body.rows).forEach(function (row) {
                    if (row.style.display === 'none') {
                        return;
                    }
                    const dayCell = row.cells[0];
                    const slots = Array.from(row.querySelectorAll('.timetable-slot, .empty-timetable-slot'));
                    if (!dayCell || !slots.length) {
                        return;
                    }
                    const rowData = Array(8).fill('');
                    rowData[0] = (dayCell.textContent || '').trim();
                    const breakCell = row.querySelector('.break-slot');
                    if (breakCell) {
                        rowData[4] = (breakCell.textContent || '').trim();
                    }
                    slots.forEach(function (slot) {
                        const periodIndex = periodOrder.indexOf(slot.dataset.period || '');
                        if (periodIndex < 0) {
                            return;
                        }
                        const value = String(slot.value || '').trim();
                        const cell = getTimeTableSlotCell(slot);
                        if (!cell || cell.style.display === 'none') {
                            return;
                        }
                        const hours = Math.max(1, Number(cell && cell.colSpan) || 1);
                        for (let offset = 0; offset < hours && periodIndex + offset < periodColumns.length; offset += 1) {
                            rowData[periodColumns[periodIndex + offset]] = value;
                        }
                    });
                    rows.push(rowData);
                });
            });
            if (rows.length === 0) {
                setStatus(timeTableStatus, 'This time table has no values to export', 'warning');
                return;
            }
            const summaryBody = tableSelector
                ? document.getElementById('mainTimeTableLoadSummary')
                : button.closest('[data-empty-timetable-card]')?.querySelector('.empty-timetable-load-summary');
            const summarySlots = Array.from(table.querySelectorAll('.timetable-slot, .empty-timetable-slot'));
            const summaryData = buildTimeTableLoadSummary(summarySlots);
            renderTimeTableLoadSummary(summarySlots, summaryBody);
            const formulaLabels = [];
            const formulaLabelKeys = new Set();
            summarySlots.forEach(function (slot) {
                if (!isVisibleFilledClassSlot(slot)) {
                    return;
                }
                const label = normalizeTimeTableDisplayValue(getComparableSubjectValue(slot.value));
                const key = getLoadSummaryType(label) + '|' + normalizeSubjectNameForSchedule(label);
                if (label && !formulaLabelKeys.has(key)) {
                    formulaLabelKeys.add(key);
                    formulaLabels.push(label);
                }
            });
            const summaryHours = summaryData.reduce(function (total, row) {
                return total + row.hours;
            }, 0);
            const summaryRows = [['Type', 'Subject / Activity', 'Hours Filled']];
            if (summaryData.length) {
                summaryData.forEach(function (row) {
                    summaryRows.push([row.type, row.label, row.hours]);
                });
                summaryRows.push(['Total', summaryHours + ' / 36 hours filled', summaryHours]);
            } else {
                summaryRows.push(['No timetable hours filled yet.', '', '']);
            }
            const individualRows = getIndividualTimeTableCards().map(function (card) {
                const meta = getIndividualTimeTableMetaFields(card);
                const facultyName = (meta.find(function (field) { return field.getAttribute('aria-label') === 'Faculty Name'; })?.value || '').trim();
                const hours = (meta.find(function (field) { return field.getAttribute('aria-label') === 'Number of hours'; })?.value || '').trim();
                const individualTable = card.querySelector('.individual-time-table');
                const output = [
                    ['Faculty', facultyName, 'Number of hours', hours],
                    Array.from(individualTable?.tHead.rows[1]?.cells || []).map(function (cell) { return (cell.textContent || '').trim(); })
                ];
                const columns = [1, 2, 3, 5, 6, 7];
                Array.from(individualTable?.tBodies[0]?.rows || []).forEach(function (row) {
                    const values = Array(8).fill('');
                    values[0] = (row.cells[0]?.textContent || '').trim();
                    values[4] = 'LUNCH BREAK';
                    getIndividualTimeTableSlots(card).filter(function (slot) { return slot.closest('tr') === row; }).forEach(function (slot) {
                        const periodIndex = periodOrder.indexOf(slot.dataset.period || '');
                        if (periodIndex < 0) return;
                        const value = String(slot.value || '').trim();
                        const cell = slot.closest('td');
                        if (!cell || cell.style.display === 'none') return;
                        const span = Math.max(1, Number(cell.colSpan) || 1);
                        for (let offset = 0; offset < span && periodIndex + offset < columns.length; offset += 1) values[columns[periodIndex + offset]] = value;
                    });
                    output.push(values);
                });
                return { name: 'Individual ' + (facultyName || 'Faculty'), rows: output, sourceRowStart: 3 };
            });
            const linkedClassRows = [{ name: 'Class Time Table', rows: rows, sourceRowStart: 2, summaryRows: summaryRows, summaryData: summaryData }];
            downloadTimeTableWorkbook(individualRows[0]?.rows || rows, individualRows[0]?.name || tableTitle, summaryRows, summaryData, [], individualRows.length ? 3 : 2, linkedClassRows.concat(individualRows.slice(1)));
            setStatus(timeTableStatus, 'Time table Excel downloaded', 'success');
        }

        function downloadIndividualTimeTableExcel(card) {
            if (!card) {
                return;
            }
            const table = card.querySelector('.individual-time-table');
            if (!table) {
                setStatus(timeTableStatus, 'Individual time table not found for download', 'warning');
                return;
            }

            const metaFields = getIndividualTimeTableMetaFields(card);
            const facultyName = (metaFields.find(function (field) {
                return field.getAttribute('aria-label') === 'Faculty Name';
            })?.value || '').trim();
            const declaredHours = (metaFields.find(function (field) {
                return field.getAttribute('aria-label') === 'Number of hours';
            })?.value || '').trim();
            const dayRows = Array.from(table.tBodies[0]?.rows || []);
            const rows = [
                ['Faculty', facultyName, 'Number of hours', declaredHours],
                Array.from(table.tHead.rows[1]?.cells || []).map(function (cell) {
                    return (cell.textContent || '').trim();
                })
            ];
            const periodColumns = [1, 2, 3, 5, 6, 7];
            const summarySlots = [];
            dayRows.forEach(function (row) {
                const rowData = Array(8).fill('');
                rowData[0] = (row.cells[0]?.textContent || '').trim();
                const slots = Array.from(row.querySelectorAll('.individual-timetable-slot'));
                slots.forEach(function (slot, periodIndex) {
                    const cell = slot.closest('td');
                    const value = String(slot.value || '').trim();
                    if (!cell || cell.style.display === 'none') {
                        return;
                    }
                    rowData[periodColumns[periodIndex]] = value;
                    const hours = Math.max(1, Number(cell.colSpan) || 1);
                    for (let offset = 1; offset < hours && periodIndex + offset < periodColumns.length; offset += 1) {
                        rowData[periodColumns[periodIndex + offset]] = value;
                    }
                    if (value) {
                        summarySlots.push({ value: value, hours: hours });
                    }
                });
                rowData[4] = 'LUNCH BREAK';
                rows.push(rowData);
            });

            const summaryByKey = new Map();
            summarySlots.forEach(function (slot) {
                const label = normalizeTimeTableDisplayValue(getComparableSubjectValue(slot.value));
                if (!label) {
                    return;
                }
                const type = getLoadSummaryType(label);
                const key = type + '|' + normalizeSubjectNameForSchedule(label);
                if (!summaryByKey.has(key)) {
                    summaryByKey.set(key, { type: type, label: label, hours: 0 });
                }
                summaryByKey.get(key).hours += slot.hours;
            });
            const summaryData = Array.from(summaryByKey.values());
            const summaryHours = summaryData.reduce(function (total, item) {
                return total + item.hours;
            }, 0);
            const summaryRows = [['Type', 'Subject / Activity', 'Hours Filled']];
            if (summaryData.length) {
                summaryData.forEach(function (item) {
                    summaryRows.push([item.type, item.label, item.hours]);
                });
                summaryRows.push(['Total', summaryHours + ' / 36 hours filled', summaryHours]);
            } else {
                summaryRows.push(['No timetable hours filled yet.', '', '']);
            }

            const title = 'Individual Time Table - ' + (facultyName || 'Faculty');
            const selectionList = getStoredSubjectSelections();
            const cardSchedule = buildIndividualFacultySchedules(selectionList).find(function (schedule) {
                const name = (getIndividualTimeTableMetaFields(card).find(function (field) { return field.getAttribute('aria-label') === 'Faculty Name'; })?.value || '').trim();
                return normalizeFacultyNameForSort(schedule.facultyName) === normalizeFacultyNameForSort(name);
            });
            const cardContext = cardSchedule && cardSchedule.selections.length
                ? getClassTimeTableContexts(selectionList).find(function (context) { return getSelectionContextKey(cardSchedule.selections[0]) === context.selectionKey; })
                : null;
            const mainButton = cardContext
                ? mainTimeTableDownloadButtons.find(function (button) { return document.querySelector(button.getAttribute('data-table-selector') || '') === cardContext.slots[0]?.closest('table'); })
                : mainTimeTableDownloadButtons[0];
            const mainTable = mainButton ? (document.querySelector(mainButton.getAttribute('data-table-selector') || '') || mainButton.closest('[data-empty-timetable-card]')?.querySelector('table.time-table-grid')) : timeTableSlots[0]?.closest('table');
            const mainRows = [];
            if (mainTable) {
                mainRows.push(Array.from(mainTable.tHead.rows[0].cells).map(function (cell) { return (cell.textContent || '').trim(); }));
                const columns = [1, 2, 3, 5, 6, 7];
                Array.from(mainTable.tBodies).forEach(function (body) {
                    Array.from(body.rows).forEach(function (row) {
                        if (row.style.display === 'none') return;
                        const values = Array(8).fill('');
                        values[0] = (row.cells[0]?.textContent || '').trim();
                        const breakCell = row.querySelector('.break-slot');
                        if (breakCell) values[4] = (breakCell.textContent || '').trim();
                        Array.from(row.querySelectorAll('.timetable-slot, .empty-timetable-slot')).forEach(function (slot) {
                            const periodIndex = periodOrder.indexOf(slot.dataset.period || '');
                            if (periodIndex < 0) return;
                            const cell = getTimeTableSlotCell(slot);
                            if (!cell || cell.style.display === 'none') return;
                            const value = String(slot.value || '').trim();
                            for (let offset = 0; offset < Math.max(1, Number(cell.colSpan) || 1) && periodIndex + offset < columns.length; offset += 1) values[columns[periodIndex + offset]] = value;
                        });
                        mainRows.push(values);
                    });
                });
            }
            const allIndividualRows = getIndividualTimeTableCards().map(function (currentCard) {
                const meta = getIndividualTimeTableMetaFields(currentCard);
                const name = (meta.find(function (field) { return field.getAttribute('aria-label') === 'Faculty Name'; })?.value || '').trim();
                const hours = (meta.find(function (field) { return field.getAttribute('aria-label') === 'Number of hours'; })?.value || '').trim();
                const individualTable = currentCard.querySelector('.individual-time-table');
                const data = [ ['Faculty', name, 'Number of hours', hours], Array.from(individualTable?.tHead.rows[1]?.cells || []).map(function (cell) { return (cell.textContent || '').trim(); }) ];
                const columns = [1, 2, 3, 5, 6, 7];
                Array.from(individualTable?.tBodies[0]?.rows || []).forEach(function (row) {
                    const values = Array(8).fill(''); values[0] = (row.cells[0]?.textContent || '').trim(); values[4] = 'LUNCH BREAK';
                    getIndividualTimeTableSlots(currentCard).filter(function (slot) { return slot.closest('tr') === row; }).forEach(function (slot) {
                        const periodIndex = periodOrder.indexOf(slot.dataset.period || ''); if (periodIndex < 0) return;
                        const cell = slot.closest('td'); if (!cell || cell.style.display === 'none') return;
                        const value = String(slot.value || '').trim();
                        for (let offset = 0; offset < Math.max(1, Number(cell.colSpan) || 1) && periodIndex + offset < columns.length; offset += 1) values[columns[periodIndex + offset]] = value;
                    }); data.push(values);
                });
                return { name: 'Individual ' + (name || 'Faculty'), rows: data, sourceRowStart: 3 };
            });
            const classSummarySlots = mainTable ? Array.from(mainTable.querySelectorAll('.timetable-slot, .empty-timetable-slot')) : [];
            const classSummaryData = buildTimeTableLoadSummary(classSummarySlots);
            const classSummaryHours = classSummaryData.reduce(function (total, item) { return total + item.hours; }, 0);
            const classSummaryRows = [['Type', 'Subject / Activity', 'Hours Filled']];
            classSummaryData.forEach(function (item) { classSummaryRows.push([item.type, item.label, item.hours]); });
            classSummaryRows.push(['Total', classSummaryHours + ' / 36 hours filled', classSummaryHours]);
            const selectedFacultyRows = allIndividualRows.find(function (item) { return item.name === 'Individual ' + (facultyName || 'Faculty'); }) || { name: title, rows: rows, sourceRowStart: 3 };
            const linkedClass = { name: 'Class Time Table', rows: mainRows.length ? mainRows : rows, sourceRowStart: 2, summaryRows: classSummaryRows, summaryData: classSummaryData };
            downloadTimeTableWorkbook(selectedFacultyRows.rows, selectedFacultyRows.name, summaryRows, summaryData, [], selectedFacultyRows.sourceRowStart || 3, [linkedClass].concat(allIndividualRows.filter(function (item) { return item !== selectedFacultyRows; })));
            setStatus(timeTableStatus, 'Individual time table Excel downloaded', 'success');
        }

        function downloadTimeTableWorkbook(rows, tableTitle, summaryRows, summaryData, formulaLabels, sourceRowStart, linkedTables) {
            const escapeXml = function (value) {
                return String(value == null ? '' : value)
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/\"/g, '&quot;')
                    .replace(/'/g, '&apos;');
            };
            const columnName = function (index) {
                let name = '';
                while (index > 0) {
                    const remainder = (index - 1) % 26;
                    name = String.fromCharCode(65 + remainder) + name;
                    index = Math.floor((index - 1) / 26);
                }
                return name;
            };
            const summaryHeaderRow = rows.length + 2;
            const summaryFirstDataRow = summaryHeaderRow + 1;
            const summaryCapacity = 36;
            const summaryTotalRow = summaryFirstDataRow + summaryCapacity;
            const summaryLastRow = summaryTotalRow;
            const summaryByLabel = new Map((summaryData || []).map(function (item) {
                return [item.label, item];
            }));
            const sortedLabels = [];
            const helperStartRow = 2;
            const helperEndRow = helperStartRow + 35;
            const helperColumns = ['B', 'C', 'D', 'F', 'G', 'H'];
            const timetableFirstRow = Number(sourceRowStart) || 2;
            const helperFormulas = new Map();
            const uniqueIndexFormulas = new Map();
            const seenHelperValues = new Set();
            let firstOccurrenceCount = 0;
            for (let index = 0; index < summaryCapacity; index += 1) {
                const dayRow = Math.floor(index / 6) + timetableFirstRow;
                const periodColumn = helperColumns[index % 6];
                const sourceAddress = periodColumn + dayRow;
                const sourceColumnIndex = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'].indexOf(periodColumn);
                const sourceValue = rows[dayRow - 1] && rows[dayRow - 1][sourceColumnIndex]
                    ? getComparableSubjectValue(rows[dayRow - 1][sourceColumnIndex])
                    : '';
                const normalizedFormula = 'IFERROR(TRIM(LEFT(' + sourceAddress + ',FIND("(LAB ROOM:",UPPER(' + sourceAddress + '))-1)),IFERROR(TRIM(LEFT(' + sourceAddress + ',FIND("(ROOM:",UPPER(' + sourceAddress + '))-1)),' + sourceAddress + '))';
                helperFormulas.set(helperStartRow + index, {
                    formula: normalizedFormula,
                    cachedValue: sourceValue
                });
                const helperRow = helperStartRow + index;
                const helperValueKey = String(sourceValue || '').toUpperCase();
                const isFirstOccurrence = Boolean(helperValueKey) && !seenHelperValues.has(helperValueKey);
                if (isFirstOccurrence) {
                    seenHelperValues.add(helperValueKey);
                    firstOccurrenceCount += 1;
                    sortedLabels.push(sourceValue);
                }
                uniqueIndexFormulas.set(helperRow, {
                    formula: 'IF(J' + helperRow + '="","",IF(COUNTIF($J$' + helperStartRow + ':J' + helperRow + ',J' + helperRow + ')=1,COUNT($K$1:K' + (helperRow - 1) + ')+1,""))',
                    cachedValue: isFirstOccurrence ? firstOccurrenceCount : ''
                });
            }
            const writeInlineCell = function (address, value, styleId) {
                return '<c r="' + address + '" t="inlineStr"' + (styleId ? ' s="' + styleId + '"' : '') + '><is><t xml:space="preserve">' + escapeXml(value) + '</t></is></c>';
            };
            const writeFormulaCell = function (address, formula, cachedValue, styleId, stringValue) {
                const typeAttribute = stringValue ? ' t="str"' : '';
                return '<c r="' + address + '"' + typeAttribute + (styleId ? ' s="' + styleId + '"' : '') + '><f>' + escapeXml(formula) + '</f><v>' + escapeXml(cachedValue) + '</v></c>';
            };
            const outputRows = new Map();
            const addCellToRow = function (rowNumber, cellXml) {
                if (!outputRows.has(rowNumber)) {
                    outputRows.set(rowNumber, []);
                }
                outputRows.get(rowNumber).push(cellXml);
            };
            rows.forEach(function (row, rowIndex) {
                const rowNumber = rowIndex + 1;
                row.forEach(function (value, columnIndex) {
                    addCellToRow(rowNumber, writeInlineCell(columnName(columnIndex + 1) + rowNumber, value, 0));
                });
            });
            const workbookSheets = [{ name: 'Time Table', rows: rows, sourceRowStart: Number(sourceRowStart) || 2, summaryRows: summaryRows, summaryData: summaryData }];
            (linkedTables || []).forEach(function (table) {
                if (table && Array.isArray(table.rows) && table.rows.length) workbookSheets.push(table);
            });
            if (workbookSheets.length > 1) {
                const sheetFiles = [];
                const sheetOverrides = [];
                const sheetRelationships = [];
                const workbookSheetEntries = [];
                workbookSheets.forEach(function (sheet, sheetIndex) {
                    const sheetId = sheetIndex + 1;
                    const sheetRows = sheet.rows;
                    const sheetSummaryData = sheet.summaryData || [];
                    const sheetSummaryRows = sheet.summaryRows || [['Type', 'Subject / Activity', 'Hours Filled']];
                    const summaryHeader = sheetSummaryRows[0] || ['Type', 'Subject / Activity', 'Hours Filled'];
                    const summaryHeaderRow = sheetRows.length + 2;
                    const summaryFirstDataRow = summaryHeaderRow + 1;
                    const totalRow = summaryFirstDataRow + summaryCapacity;
                    const firstRow = Number(sheet.sourceRowStart) || 2;
                    const sheetOutput = new Map();
                    const put = function (rowNo, xml) {
                        if (!sheetOutput.has(rowNo)) sheetOutput.set(rowNo, []);
                        sheetOutput.get(rowNo).push(xml);
                    };
                    sheetRows.forEach(function (row, rowIdx) {
                        row.forEach(function (value, columnIdx) {
                            const addr = columnName(columnIdx + 1) + (rowIdx + 1);
                            put(rowIdx + 1, writeInlineCell(addr, value, rowIdx === 0 ? 1 : 0));
                        });
                    });
                    summaryHeader.forEach(function (value, columnIdx) { put(summaryHeaderRow, writeInlineCell(columnName(columnIdx + 1) + summaryHeaderRow, value, 1)); });
                    const sources = [];
                    const helperCols = ['B', 'C', 'D', 'F', 'G', 'H'];
                    const seen = new Map();
                    for (let idx = 0; idx < 36; idx += 1) {
                        const dayRow = Math.floor(idx / 6) + firstRow;
                        const col = helperCols[idx % 6];
                        const colIdx = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'].indexOf(col);
                        const raw = sheetRows[dayRow - 1] && sheetRows[dayRow - 1][colIdx] ? getComparableSubjectValue(sheetRows[dayRow - 1][colIdx]) : '';
                        const addr = col + dayRow;
                        const formula = 'IFERROR(TRIM(LEFT(' + addr + ',FIND("(LAB ROOM:",UPPER(' + addr + '))-1)),IFERROR(TRIM(LEFT(' + addr + ',FIND("(ROOM:",UPPER(' + addr + '))-1)),' + addr + '))';
                        const helperRow = 2 + idx;
                        put(helperRow, writeFormulaCell('J' + helperRow, formula, raw, 0, true));
                        const key = String(raw || '').toUpperCase();
                        let uniqueNumber = '';
                        if (key) { if (!seen.has(key)) seen.set(key, seen.size + 1); uniqueNumber = seen.get(key); }
                        put(helperRow, writeFormulaCell('K' + helperRow, 'IF(J' + helperRow + '="","",IF(COUNTIF($J$2:J' + helperRow + ',J' + helperRow + ')=1,COUNT($K$1:K' + (helperRow - 1) + ')+1,""))', uniqueNumber, 0, false));
                        if (key && !sources.some(function (entry) { return entry.key === key; })) sources.push({ key: key, label: raw, number: seen.get(key), item: sheetSummaryData.find(function (entry) { return normalizeSubjectNameForSchedule(entry.label) === normalizeSubjectNameForSchedule(raw); }) });
                    }
                    for (let idx = 0; idx < summaryCapacity; idx += 1) {
                        const rowNo = summaryFirstDataRow + idx;
                        const entry = sources[idx];
                        const subjectFormula = 'IFERROR(INDEX($J$2:$J$37,MATCH(ROWS($B$' + summaryFirstDataRow + ':B' + rowNo + '),$K$2:$K$37,0)),"")';
                        const typeFormula = 'IF(B' + rowNo + '="","",IF(ISNUMBER(SEARCH("SPORTS",B' + rowNo + ')),"Sports",IF(ISNUMBER(SEARCH("LIBRARY",B' + rowNo + ')),"Library",IF(ISNUMBER(SEARCH("MENTORING",B' + rowNo + ')),"Mentoring",IF(ISNUMBER(SEARCH("SEMINAR",B' + rowNo + ')),"Seminar",IF(ISNUMBER(SEARCH("INTERNSHIP",B' + rowNo + ')),"Internship",IF(OR(ISNUMBER(SEARCH("LAB",B' + rowNo + ')),ISNUMBER(SEARCH("IOMPI",B' + rowNo + '))),"Lab","Subject")))))))';
                        put(rowNo, writeFormulaCell('A' + rowNo, typeFormula, entry ? (entry.item?.type || getLoadSummaryType(entry.label)) : '', 0, true));
                        put(rowNo, writeFormulaCell('B' + rowNo, subjectFormula, entry ? entry.label : '', 0, true));
                        put(rowNo, writeFormulaCell('C' + rowNo, 'IF(B' + rowNo + '="","",COUNTIF($J$2:$J$37,B' + rowNo + '))', entry?.item?.hours || '', 0, false));
                    }
                    const total = sheetSummaryData.reduce(function (sum, item) { return sum + item.hours; }, 0);
                    put(totalRow, writeInlineCell('A' + totalRow, 'Total', 2));
                    put(totalRow, writeFormulaCell('B' + totalRow, 'C' + totalRow + '&" / 36 hours filled"', total + ' / 36 hours filled', 2, true));
                    put(totalRow, writeFormulaCell('C' + totalRow, 'COUNTIF($J$2:$J$37,"?*")', total, 2, false));
                    const lastRow = totalRow;
                    const xmlRows = Array.from({ length: lastRow }, function (_, idx) {
                        const rowNo = idx + 1;
                        const cells = sheetOutput.get(rowNo) || [];
                        cells.sort(function (left, right) { return left.match(/r="([A-Z]+)(\d+)"/)[1].localeCompare(right.match(/r="([A-Z]+)(\d+)"/)[1]); });
                        return '<row r="' + rowNo + '">' + cells.join('') + '</row>';
                    }).join('');
                    const sheetName = String(sheet.name || ('Time Table ' + sheetId)).replace(/[\\/*?:\[\]]/g, ' ').slice(0, 31);
                    workbookSheetEntries.push('<sheet name="' + escapeXml(sheetName) + '" sheetId="' + sheetId + '" r:id="rId' + sheetId + '"/>');
                    sheetRelationships.push('<Relationship Id="rId' + sheetId + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet' + sheetId + '.xml"/>');
                    sheetOverrides.push('<Override PartName="/xl/worksheets/sheet' + sheetId + '.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>');
                    sheetFiles.push({ name: 'xl/worksheets/sheet' + sheetId + '.xml', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><cols><col min="10" max="11" width="2" hidden="1" customWidth="1"/></cols><sheetData>' + xmlRows + '</sheetData></worksheet>' });
                });
                const linkedFiles = [
                    { name: '[Content_Types].xml', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>' + sheetOverrides.join('') + '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>' },
                    { name: '_rels/.rels', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>' },
                    { name: 'xl/workbook.xml', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' + workbookSheetEntries.join('') + '</sheets><calcPr calcId="0" calcMode="auto" fullCalcOnLoad="1" forceFullCalc="1" calcOnSave="1"/></workbook>' },
                    { name: 'xl/_rels/workbook.xml.rels', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + sheetRelationships.join('') + '<Relationship Id="rId' + (workbookSheets.length + 1) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>' },
                    { name: 'xl/styles.xml', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="3"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FF1F3B5B"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FF111111"/><name val="Calibri"/></font></fonts><fills count="4"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFE8F1FE"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFF2CC"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border><left style="thin"><color rgb="FFD9E6F5"/></left><right style="thin"><color rgb="FFD9E6F5"/></right><top style="thin"><color rgb="FFD9E6F5"/></top><bottom style="thin"><color rgb="FFD9E6F5"/></bottom><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/><xf numFmtId="0" fontId="2" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></styleSheet>' }
                ].concat(sheetFiles);
                const linkedTitle = (tableTitle || 'Time_Table').replace(/[^^\w-]+/g, '_').replace(/^_+|_+$/g, '') || 'Time_Table';
                createStoredZip(linkedFiles).then(function (blob) {
                    const link = document.createElement('a'); const downloadUrl = URL.createObjectURL(blob); link.href = downloadUrl; link.download = linkedTitle + '_and_individuals.xlsx'; document.body.appendChild(link); link.click(); link.remove(); window.setTimeout(function () { URL.revokeObjectURL(downloadUrl); }, 1000);
                }).catch(function (error) { console.error('Failed to create linked timetable workbook', error); setStatus(timeTableStatus, 'Could not create the Excel file. Please try again.', 'warning'); });
                return;
            }
            const summaryHeader = (summaryRows && summaryRows[0]) || ['Type', 'Subject / Activity', 'Hours Filled'];
            summaryHeader.forEach(function (value, columnIndex) {
                addCellToRow(summaryHeaderRow, writeInlineCell(columnName(columnIndex + 1) + summaryHeaderRow, value, 1));
            });
            const makeSubjectFormula = function (rowNumber) {
                // Use legacy-compatible formulas so changes recalculate in older Excel versions too.
                return 'IFERROR(INDEX($J$' + helperStartRow + ':$J$' + helperEndRow + ',MATCH(ROWS($B$' + summaryFirstDataRow + ':B' + rowNumber + '),$K$' + helperStartRow + ':$K$' + helperEndRow + ',0)),"")';
            };
            for (let index = 0; index < summaryCapacity; index += 1) {
                const rowNumber = summaryFirstDataRow + index;
                const label = sortedLabels[index] || '';
                const item = summaryByLabel.get(label);
                const typeFormula = 'IF(B' + rowNumber + '="","",IF(ISNUMBER(SEARCH("SPORTS",B' + rowNumber + ')),"Sports",IF(ISNUMBER(SEARCH("LIBRARY",B' + rowNumber + ')),"Library",IF(ISNUMBER(SEARCH("MENTORING",B' + rowNumber + ')),"Mentoring",IF(ISNUMBER(SEARCH("SEMINAR",B' + rowNumber + ')),"Seminar",IF(ISNUMBER(SEARCH("INTERNSHIP",B' + rowNumber + ')),"Internship",IF(OR(ISNUMBER(SEARCH("LAB",B' + rowNumber + ')),ISNUMBER(SEARCH("IOMPI",B' + rowNumber + '))),"Lab","Subject")))))))';
                addCellToRow(rowNumber, writeFormulaCell('A' + rowNumber, typeFormula, item ? item.type : '', 0, true));
                addCellToRow(rowNumber, writeFormulaCell('B' + rowNumber, makeSubjectFormula(rowNumber), label, 0, true));
                addCellToRow(rowNumber, writeFormulaCell('C' + rowNumber, 'IF(B' + rowNumber + '="","",COUNTIF($J$' + helperStartRow + ':$J$' + helperEndRow + ',B' + rowNumber + '))', item ? item.hours : '', 0, false));
            }
            const cachedTotal = (summaryData || []).reduce(function (total, item) {
                return total + item.hours;
            }, 0);
            addCellToRow(summaryTotalRow, writeInlineCell('A' + summaryTotalRow, 'Total', 2));
            addCellToRow(summaryTotalRow, writeFormulaCell('B' + summaryTotalRow, 'C' + summaryTotalRow + '&" / 36 hours filled"', cachedTotal + ' / 36 hours filled', 2, true));
            // Count occupied timetable periods directly so the total follows slot edits
            // even when the distinct-subject list above changes length.
            addCellToRow(summaryTotalRow, writeFormulaCell('C' + summaryTotalRow, 'COUNTIF($J$' + helperStartRow + ':$J$' + helperEndRow + ',"?*")', cachedTotal, 2, false));
            helperFormulas.forEach(function (source, rowNumber) {
                addCellToRow(rowNumber, writeFormulaCell('J' + rowNumber, source.formula, source.cachedValue, 0, true));
            });
            uniqueIndexFormulas.forEach(function (source, rowNumber) {
                addCellToRow(rowNumber, writeFormulaCell('K' + rowNumber, source.formula, source.cachedValue, 0, false));
            });
            const sheetRows = Array.from({ length: summaryLastRow }, function (_, index) {
                const rowNumber = index + 1;
                const cells = outputRows.get(rowNumber) || [];
                cells.sort(function (left, right) {
                    const leftAddress = left.match(/r="([A-Z]+)(\d+)"/)[1];
                    const rightAddress = right.match(/r="([A-Z]+)(\d+)"/)[1];
                    return leftAddress.localeCompare(rightAddress);
                });
                return '<row r="' + rowNumber + '">' + cells.join('') + '</row>';
            }).join('');
            const safeTitle = tableTitle.replace(/[^\w-]+/g, '_').replace(/^_+|_+$/g, '') || 'Time_Table';
            const files = [
                { name: '[Content_Types].xml', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>' },
                { name: '_rels/.rels', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>' },
                { name: 'xl/workbook.xml', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Time Table" sheetId="1" r:id="rId1"/></sheets><calcPr calcId="0" calcMode="auto" fullCalcOnLoad="1" forceFullCalc="1" calcOnSave="1"/></workbook>' },
                { name: 'xl/_rels/workbook.xml.rels', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>' },
                { name: 'xl/styles.xml', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="3"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FF1F3B5B"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FF111111"/><name val="Calibri"/></font></fonts><fills count="4"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFE8F1FE"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFF2CC"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border><left style="thin"><color rgb="FFD9E6F5"/></left><right style="thin"><color rgb="FFD9E6F5"/></right><top style="thin"><color rgb="FFD9E6F5"/></top><bottom style="thin"><color rgb="FFD9E6F5"/></bottom><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/><xf numFmtId="0" fontId="2" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>' },
                { name: 'xl/worksheets/sheet1.xml', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><cols><col min="10" max="11" width="2" hidden="1" customWidth="1"/></cols><sheetData>' + sheetRows + '</sheetData></worksheet>' }
            ];
            createStoredZip(files).then(function (blob) {
                const link = document.createElement('a');
                const downloadUrl = URL.createObjectURL(blob);
                link.href = downloadUrl;
                link.download = safeTitle + '.xlsx';
                document.body.appendChild(link);
                link.click();
                link.remove();
                window.setTimeout(function () { URL.revokeObjectURL(downloadUrl); }, 1000);
            }).catch(function (error) {
                console.error('Failed to create timetable workbook', error);
                setStatus(timeTableStatus, 'Could not create the Excel file. Please try again.', 'warning');
            });
        }

        function createStoredZip(files) {
            const encoder = new TextEncoder();
            const crcTable = createCrc32Table();
            const crc32 = function (bytes) {
                let crc = 0xffffffff;
                for (let i = 0; i < bytes.length; i += 1) {
                    crc = (crc >>> 8) ^ crcTable[(crc ^ bytes[i]) & 0xff];
                }
                return (crc ^ 0xffffffff) >>> 0;
            };
            const u16 = function (value) { return [value & 0xff, (value >>> 8) & 0xff]; };
            const u32 = function (value) { return [value & 0xff, (value >>> 8) & 0xff, (value >>> 16) & 0xff, (value >>> 24) & 0xff]; };
            const concat = function (parts) {
                const size = parts.reduce(function (total, part) { return total + part.length; }, 0);
                const result = new Uint8Array(size);
                let offset = 0;
                parts.forEach(function (part) { result.set(part, offset); offset += part.length; });
                return result;
            };
            const localParts = [];
            const centralParts = [];
            let offset = 0;
            files.forEach(function (file) {
                const name = encoder.encode(file.name);
                const data = encoder.encode(file.content);
                const crc = crc32(data);
                const localHeader = concat([new Uint8Array(u32(0x04034b50)), new Uint8Array(u16(20)), new Uint8Array(u16(0x0800)), new Uint8Array(u16(0)), new Uint8Array(u16(0)), new Uint8Array(u16(0)), new Uint8Array(u32(crc)), new Uint8Array(u32(data.length)), new Uint8Array(u32(data.length)), new Uint8Array(u16(name.length)), new Uint8Array(u16(0)), name]);
                localParts.push(localHeader, data);
                const centralHeader = concat([new Uint8Array(u32(0x02014b50)), new Uint8Array(u16(20)), new Uint8Array(u16(20)), new Uint8Array(u16(0x0800)), new Uint8Array(u16(0)), new Uint8Array(u16(0)), new Uint8Array(u16(0)), new Uint8Array(u32(crc)), new Uint8Array(u32(data.length)), new Uint8Array(u32(data.length)), new Uint8Array(u16(name.length)), new Uint8Array(u16(0)), new Uint8Array(u16(0)), new Uint8Array(u16(0)), new Uint8Array(u16(0)), new Uint8Array(u32(0)), new Uint8Array(u32(offset)), name]);
                centralParts.push(centralHeader);
                offset += localHeader.length + data.length;
            });
            const centralDirectory = concat(centralParts);
            const end = new Uint8Array(u32(0x06054b50).concat(u16(0), u16(0), u16(files.length), u16(files.length), u32(centralDirectory.length), u32(offset), u16(0)));
            return Promise.resolve(new Blob([concat(localParts), centralDirectory, end], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
        }

        function createCrc32Table() {
            const table = new Uint32Array(256);
            for (let i = 0; i < 256; i += 1) {
                let value = i;
                for (let bit = 0; bit < 8; bit += 1) {
                    value = value & 1 ? (0xedb88320 ^ (value >>> 1)) : (value >>> 1);
                }
                table[i] = value >>> 0;
            }
            return table;
        }

        function clearAllTimeTableSlotValues() {
            const slotGroups = [
                timeTableSlots,
                getIndividualTimeTableSlots(),
                getEmptyTimeTableSlots()
            ];
            slotGroups.forEach(function (slots) {
                resetClassTimeTableMerges(slots);
                (slots || []).forEach(function (slot) {
                    slot.value = '';
                });
            });
            resetClassTimeTableMerges(getIndividualTimeTableSlots());
            resetClassTimeTableMerges(getEmptyTimeTableSlots());
            resetLabTimeTable();
            getIndividualTimeTableMetaFields().forEach(function (field) {
                field.value = '';
            });
        }

        function clearTimeTableData() {
            if (hasTimeTableContent() && !confirm('Clear the saved timetable and all period entries?')) {
                return;
            }
            localStorage.removeItem(timeTableStorageKey);
            clearAllTimeTableSlotValues();
            renderAllTimeTableLoadSummaries();
            resetLabTimeTable();
            setStatus(timeTableStatus, 'Timetable cleared', 'muted');
        }

        function getSubjectSelectionPayload() {
            const selectedOption = subjectSelectionFields.subjectName && subjectSelectionFields.subjectName.selectedIndex >= 0
                ? subjectSelectionFields.subjectName.options[subjectSelectionFields.subjectName.selectedIndex]
                : null;

            return {
                facultyName: subjectSelectionFields.facultyName.value.trim(),
                employeeCode: subjectSelectionFields.employeeCode.value.trim(),
                branch: subjectSelectionFields.branch.value,
                section: subjectSelectionFields.section.value || 'A',
                regulation: subjectSelectionFields.regulation.value || 'R22',
                year: subjectSelectionFields.year.value,
                semester: subjectSelectionFields.semester.value,
                subjectName: subjectSelectionFields.subjectName.value,
                subjectCode: selectedOption ? (selectedOption.dataset.code || '') : '',
                labRoomNumber: subjectSelectionFields.labRoomNumber.value,
                timesTaught: subjectSelectionFields.timesTaught.value.trim(),
                previousResult: subjectSelectionFields.previousResult.value.trim(),
                savedAt: new Date().toISOString()
            };
        }

        function setSubjectSelectionFields(payload) {
            const data = payload || {};
            subjectSelectionFields.facultyName.value = data.facultyName || '';
            subjectSelectionFields.employeeCode.value = data.employeeCode || '';
            subjectSelectionFields.branch.value = data.branch || subjectSelectionFields.branch.value || 'IT';
            subjectSelectionFields.section.value = data.section || subjectSelectionFields.section.value || 'A';
            subjectSelectionFields.regulation.value = data.regulation || subjectSelectionFields.regulation.value || 'R22';
            subjectSelectionFields.year.value = data.year || subjectSelectionFields.year.value || '3';
            subjectSelectionFields.semester.value = data.semester || subjectSelectionFields.semester.value || '1';
            subjectSelectionFields.labRoomNumber.value = data.labRoomNumber || '';
            subjectSelectionFields.timesTaught.value = data.timesTaught || '';
            subjectSelectionFields.previousResult.value = data.previousResult || '';
            loadSubjectSelectionSubjects(data.subjectName || '');
        }

        function normalizeSubjectSelections(payload) {
            if (Array.isArray(payload)) {
                return payload.filter(function (entry) {
                    return entry && (entry.facultyName || entry.employeeCode || entry.subjectName);
                }).map(function (entry) {
                    return Object.assign({ regulation: 'R22' }, entry, { regulation: entry.regulation || 'R22' });
                });
            }
            if (payload && (payload.facultyName || payload.employeeCode || payload.subjectName)) {
                return [Object.assign({ regulation: 'R22' }, payload, { regulation: payload.regulation || 'R22' })];
            }
            return [];
        }

        function normalizeFacultyNameForSort(name) {
            return normalizeSubjectNameForSchedule(name || '').replace(/[^A-Z0-9]/g, '');
        }

        function sortSubjectSelectionsByFaculty(selections) {
            return normalizeSubjectSelections(selections).map(function (selection, index) {
                return {
                    selection: selection,
                    index: index,
                    facultyKey: normalizeFacultyNameForSort(selection.facultyName),
                    employeeKey: normalizeClassValue(selection.employeeCode || ''),
                    branchKey: normalizeClassValue(selection.branch || ''),
                    sectionKey: normalizeClassValue(selection.section || 'A'),
                    yearKey: normalizeClassValue(selection.year || ''),
                    semesterKey: normalizeClassValue(selection.semester || ''),
                    subjectKey: normalizeSubjectNameForSchedule(selection.subjectName || '')
                };
            }).sort(function (left, right) {
                return left.facultyKey.localeCompare(right.facultyKey) ||
                    left.employeeKey.localeCompare(right.employeeKey) ||
                    left.branchKey.localeCompare(right.branchKey) ||
                    left.sectionKey.localeCompare(right.sectionKey) ||
                    left.yearKey.localeCompare(right.yearKey) ||
                    left.semesterKey.localeCompare(right.semesterKey) ||
                    left.subjectKey.localeCompare(right.subjectKey) ||
                    left.index - right.index;
            }).map(function (entry) {
                return entry.selection;
            });
        }

        function getStoredSubjectSelections() {
            const saved = localStorage.getItem(subjectSelectionStorageKey);
            if (!saved) {
                return [];
            }
            try {
                return normalizeSubjectSelections(JSON.parse(saved));
            } catch (error) {
                console.error('Failed to load saved faculty subject selections', error);
                return [];
            }
        }

        function storeSubjectSelections(selections) {
            localStorage.setItem(subjectSelectionStorageKey, JSON.stringify(sortSubjectSelectionsByFaculty(selections)));
        }

        function getSubjectSelectionDuplicateKey(selection) {
            return [
                normalizeClassValue(selection.regulation || 'R22'),
                normalizeClassValue(selection.branch || ''),
                normalizeClassValue(selection.section || 'A'),
                normalizeAcademicLevelValue(selection.year || ''),
                normalizeAcademicLevelValue(selection.semester || ''),
                normalizeClassValue(selection.subjectCode || '') || normalizeSubjectNameForSchedule(selection.subjectName || '')
            ].join('|');
        }

        function isLabSubjectSelection(selection) {
            const subjectName = selection.subjectName || '';
            const subjectCode = normalizeClassValue(selection.subjectCode || '');
            const labSubjectCodes = new Set([
                'IT504PC',
                'IT505PC',
                'IT532PE',
                '2512302',
                '2504311',
                '2505308',
                '2599302',
                'CS507PC',
                'IT705PC',
                'AM705PC'
            ]);

            return isLaboratorySubject(subjectName) ||
                isLaboratorySubject(getShortSubjectLabel(subjectName)) ||
                labSubjectCodes.has(subjectCode) ||
                getScheduleLabelsForSelection(selection).some(function (label) {
                    return isLaboratorySubject(label);
                });
        }

        function shouldCheckSubjectSelectionDuplicate(selection) {
            return !isLabSubjectSelection(selection);
        }

        function findDuplicateSubjectSelection(payload, selections) {
            if (!shouldCheckSubjectSelectionDuplicate(payload)) {
                return null;
            }
            const payloadKey = getSubjectSelectionDuplicateKey(payload);
            return normalizeSubjectSelections(selections).find(function (selection) {
                if (!shouldCheckSubjectSelectionDuplicate(selection)) {
                    return false;
                }
                return getSubjectSelectionDuplicateKey(selection) === payloadKey;
            }) || null;
        }

        function alertDuplicateSubjectSelection(payload, duplicateSelection) {
            if (!shouldCheckSubjectSelectionDuplicate(payload)) {
                return;
            }
            const subjectLabel = payload.subjectCode
                ? payload.subjectCode + ' - ' + payload.subjectName
                : payload.subjectName;
            const message = subjectLabel + ' is already chosen for ' +
                (payload.regulation || 'R22') + ' ' +
                getYearSemLabel(payload.year, payload.semester) + ' ' +
                getBranchDisplayLabel(payload.branch) + ' Section ' +
                (payload.section || 'A') +
                '. A subject can be assigned only once per section.';
            window.alert(message);
            setStatus(subjectSelectionStatus, message, 'warning');
            if (duplicateSelection && duplicateSelection.facultyName) {
                console.warn('Duplicate subject selection already assigned to:', duplicateSelection.facultyName);
            }
        }

        function updateSubjectSelectionCount(count) {
            if (subjectSelectionCount) {
                subjectSelectionCount.textContent = String(count || 0);
            }
        }

        function renderSubjectSelectionPreview(payload) {
            const selections = sortSubjectSelectionsByFaculty(payload);
            subjectSelectionPreviewBody.innerHTML = '';
            updateSubjectSelectionCount(selections.length);
            renderCourseReference(selections);

            if (!selections.length) {
                const emptyRow = document.createElement('tr');
                const emptyCell = document.createElement('td');
                emptyCell.colSpan = 12;
                emptyCell.className = 'text-center text-muted';
                emptyCell.textContent = 'No subject selection saved yet.';
                emptyRow.appendChild(emptyCell);
                subjectSelectionPreviewBody.appendChild(emptyRow);
                return;
            }

            selections.forEach(function (payload, index) {
                const row = document.createElement('tr');
                [
                    String(index + 1),
                    payload.facultyName || '-',
                    payload.employeeCode || '-',
                    payload.branch || '-',
                    payload.section || 'A',
                    payload.regulation || 'R22',
                    payload.year || '-',
                    payload.semester || '-',
                    payload.subjectCode ? getSubjectDisplayLabel(payload.subjectCode, payload.subjectName) : getSubjectShortDisplayName(payload.subjectCode, payload.subjectName),
                    payload.labRoomNumber || '-',
                    payload.timesTaught || '0'
                ].forEach(function (value) {
                    const cell = document.createElement('td');
                    cell.textContent = value;
                    row.appendChild(cell);
                });
                const resultActionCell = document.createElement('td');
                const resultText = document.createElement('span');
                const deleteButton = document.createElement('button');
                resultActionCell.className = 'subject-selection-result-action';
                resultText.textContent = payload.previousResult || '-';
                deleteButton.type = 'button';
                deleteButton.className = 'btn exam-btn exam-btn-danger btn-sm subject-selection-delete-btn';
                deleteButton.dataset.index = String(index);
                deleteButton.innerHTML = '<i class="fas fa-trash me-1"></i>Delete';
                resultActionCell.appendChild(resultText);
                resultActionCell.appendChild(deleteButton);
                row.appendChild(resultActionCell);
                subjectSelectionPreviewBody.appendChild(row);
            });
        }

        function renderCourseReference(payload) {
            if (!courseReferenceBody) {
                return;
            }

            const selections = getTimeTableClassSelections(payload);
            courseReferenceBody.innerHTML = '';

            if (!selections.length) {
                const emptyRow = document.createElement('tr');
                const emptyCell = document.createElement('td');
                emptyCell.colSpan = 4;
                emptyCell.className = 'text-center text-muted';
                emptyCell.textContent = 'Add faculty selections to display subjects here.';
                emptyRow.appendChild(emptyCell);
                courseReferenceBody.appendChild(emptyRow);
                return;
            }

            selections.forEach(function (selection, index) {
                const row = document.createElement('tr');
                [
                    String(index + 1),
                    selection.subjectCode || '-',
                    getSubjectShortDisplayName(selection.subjectCode, selection.subjectName),
                    selection.facultyName || '-'
                ].forEach(function (value) {
                    const cell = document.createElement('td');
                    cell.textContent = value;
                    row.appendChild(cell);
                });
                courseReferenceBody.appendChild(row);
            });
        }

        function saveSubjectSelection(event) {
            event.preventDefault();
            const payload = getSubjectSelectionPayload();

            if (!payload.facultyName || !payload.employeeCode || !payload.subjectName) {
                setStatus(subjectSelectionStatus, 'Faculty name, employee code, and subject are required', 'warning');
                return;
            }

            const duplicateSelection = findDuplicateSubjectSelection(payload, getStoredSubjectSelections());
            if (duplicateSelection) {
                alertDuplicateSubjectSelection(payload, duplicateSelection);
                return;
            }

            storeSubjectSelections([payload]);
            renderSubjectSelectionPreview([payload]);
            setStatus(subjectSelectionStatus, 'Subject selection saved at ' + formatSavedTime(payload.savedAt), 'success');
        }

        function addFacultySubjectSelection() {
            const payload = getSubjectSelectionPayload();
            if (!payload.facultyName || !payload.employeeCode || !payload.subjectName) {
                setStatus(subjectSelectionStatus, 'Faculty name, employee code, and subject are required before adding faculty', 'warning');
                return;
            }

            const selections = getStoredSubjectSelections();
            const duplicateSelection = findDuplicateSubjectSelection(payload, selections);
            if (duplicateSelection) {
                alertDuplicateSubjectSelection(payload, duplicateSelection);
                return;
            }
            selections.push(payload);

            storeSubjectSelections(selections);
            renderSubjectSelectionPreview(selections);
            setStatus(subjectSelectionStatus, 'Faculty added as row ' + selections.length + ' below existing details', 'success');
            setSubjectSelectionFields({
                branch: payload.branch,
                year: payload.year,
                semester: payload.semester
            });
        }

        function regenerateTimeTableFromStoredSelections() {
            const selections = getStoredSubjectSelections();
            const classContexts = getClassTimeTableContexts(selections);
            const facultyOccupancyMap = createFacultyOccupancyMap();
            const labRoomOccupancyMap = createLabRoomOccupancyMap();
            prePopulateOccupancyMapsFromExistingData(facultyOccupancyMap, labRoomOccupancyMap);
            applyTimeTableRequirementRepairs(classContexts, selections);
            repairAllClassLabRoomConflicts(classContexts, selections);
            repairAllFacultyConflicts(classContexts, selections);
            fillAllClassBlankSlots(classContexts, selections);
            repairAllTimetableResourceConflicts(classContexts, selections);
            syncIndividualTimeTablesWithMainTables(selections, classContexts);
            normalizeAllTimeTableSlotValues();
            markTimeTableDirty();
            saveTimeTableData();
        }

        function deleteFacultySubjectSelection(index) {
            const selections = getStoredSubjectSelections();
            if (index < 0 || index >= selections.length) {
                return;
            }

            const removed = selections.splice(index, 1)[0];
            storeSubjectSelections(selections);
            renderSubjectSelectionPreview(selections);
            setStatus(
                subjectSelectionStatus,
                'Deleted ' + ((removed && removed.facultyName) || 'faculty') + ' from available faculties',
                'warning'
            );

            if (!selections.length) {
                localStorage.removeItem(timeTableStorageKey);
                clearAllTimeTableSlotValues();
                renderAllTimeTableLoadSummaries();
                setStatus(
                    timeTableStatus,
                    'All faculty selections deleted - main, individual and lab timetables cleared',
                    'muted'
                );
                return;
            }

            regenerateTimeTableFromStoredSelections();
            setStatus(
                timeTableStatus,
                'Time Table entries for the deleted faculty were also removed',
                'success'
            );
        }

        function loadSubjectSelection() {
            const saved = localStorage.getItem(subjectSelectionStorageKey);
            if (!saved) {
                loadSubjectSelectionSubjects();
                renderSubjectSelectionPreview(null);
                setStatus(subjectSelectionStatus, 'Subject selection not saved yet', 'muted');
                return;
            }

            try {
                const selections = normalizeSubjectSelections(JSON.parse(saved));
                setSubjectSelectionFields(selections[0] || {});
                renderSubjectSelectionPreview(selections);
                setStatus(subjectSelectionStatus, selections.length + ' faculty selection(s) loaded', 'success');
            } catch (error) {
                console.error('Failed to load subject selection', error);
                loadSubjectSelectionSubjects();
                renderSubjectSelectionPreview(null);
                setStatus(subjectSelectionStatus, 'Could not read saved subject selection', 'warning');
            }
        }

        function clearSubjectSelection() {
            if (!confirm('Clear the saved faculty subject selection?')) {
                return;
            }
            localStorage.removeItem(subjectSelectionStorageKey);
            setSubjectSelectionFields({});
            renderSubjectSelectionPreview(null);
            localStorage.removeItem(timeTableStorageKey);
            clearAllTimeTableSlotValues();
            renderAllTimeTableLoadSummaries();
            resetLabTimeTable();
            setStatus(timeTableStatus, 'Timetable cleared', 'muted');
            setStatus(subjectSelectionStatus, 'Subject selection cleared', 'muted');
        }

        function switchToTimeTableTab() {
            const timeTableTabButton = document.getElementById('timetable-tab');
            if (!timeTableTabButton) {
                return;
            }

            try {
                if (window.bootstrap && window.bootstrap.Tab) {
                    window.bootstrap.Tab.getOrCreateInstance(timeTableTabButton).show();
                } else {
                    timeTableTabButton.click();
                }
            } catch (e) {
                document.querySelectorAll('.nav-link').forEach(function(btn) {
                    btn.classList.remove('active');
                    btn.setAttribute('aria-selected', 'false');
                });
                document.querySelectorAll('.tab-pane').forEach(function(pane) {
                    pane.classList.remove('active', 'show', 'fade');
                });
                timeTableTabButton.classList.add('active');
                timeTableTabButton.setAttribute('aria-selected', 'true');
                const pane = document.getElementById('timetable');
                if (pane) {
                    pane.classList.add('active', 'show', 'fade');
                }
            }

            const timetablePane = document.getElementById('timetable');
            if (timetablePane) {
                setTimeout(function() {
                    timetablePane.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 80);
            }
        }

        function isLaboratorySubject(subjectName) {
            return /\b(lab|laboratory)\b/i.test(subjectName || '') ||
                /\bes\s*lab\b|\bdm\s*lab\b|\bcd\s*lab\b|flutter\s*lab|\bsdc\s*lab\b/i.test(subjectName || '') ||
                /skill development course|ui design flutter|project\s*stage\s*[-–]?\s*i\b|project\s*stage\s*1\b/i.test(subjectName || '') ||
                /\biompi\b/i.test(subjectName || '');
        }

        function isLaboratoryScheduleValue(subjectName) {
            const comparableName = getComparableSubjectValue(subjectName || '');
            const label = comparableName.split(' - ').pop().trim();
            const normalizedName = normalizeSubjectNameForSchedule(label);
            const roomMatch = String(subjectName || '').match(/\(\s*ROOM:\s*([^)]+)\)/i);
            const isRoomAssignedSoftwareEngineeringLab = normalizedName === 'SE' && roomMatch &&
                normalizeClassValue(roomMatch[1]) === 'D-314';
            return isLaboratorySubject(comparableName) || isLaboratorySubject(label) ||
                Boolean(isRoomAssignedSoftwareEngineeringLab) ||
                normalizedName === 'INT' || normalizedName === 'INTERNSHIP' || normalizedName.indexOf('INTERNSHIP') !== -1;
        }

        function getShortSubjectLabel(subjectName) {
            const trimmedName = String(subjectName || '').trim();
            if (!trimmedName) {
                return '';
            }
            if (/^(SPORTS|LIBRARY|MENTORING)$/i.test(trimmedName)) {
                return trimmedName.toUpperCase();
            }
            const canonicalShortLabels = {
                'KNOWLEDGE REPRESENTATION AND REASONING': 'KRAR',
                'DATA ANALYTICS': 'DA',
                'NATURAL LANGUAGE PROCESSING': 'NLP',
                'HUMAN COMPUTER INTERACTION': 'HCI',
                'RENEWABLE ENERGY SOURCES': 'RES',
                'NATURAL LANGUAGE PROCESSING LAB': 'NLP Lab',
                'NATURAL LANGUAGE PROCESSING LABORATORY': 'NLP Lab',
                'NLP LABORATORY': 'NLP Lab',
                'DATA ANALYTICS LABORATORY': 'DA Lab',
                'ADVANCED ENGLISH COMMUNICATION SKILLS LAB': 'AECS Lab',
                'ADVANCED ENGLISH COMMUNICATION SKILLS LABORATORY': 'AECS Lab',
                'INDUSTRIAL ORIENTED MINI PROJECT/ INTERNSHIP': 'INTERNSHIP',
                'ENVIRONMENTAL SCIENCE': 'EVS/IKS',
                'ENVIRONMENTAL SCIENCE / INDIAN KNOWLEDGE SYSTEM': 'EVS/IKS',
                'ENVIRONMENTAL SCIENCE/INDIAN KNOWLEDGE SYSTEM': 'EVS/IKS',
                'INDIAN KNOWLEDGE SYSTEM': 'EVS/IKS',
                'VALUE ETHICS AND GENDER SENSITIZATION': 'VEGS',
                'VALUE ETHICS / GENDER SENSITIZATION': 'VEGS',
                'GENDER SENSITIZATION / HUMAN VALUES AND PROFESSIONAL ETHICS': 'VEGS',
                'EVS/IKS': 'EVS/IKS',
                'VEGS': 'VEGS',
                'MSF': 'MSF',
                'INTERNSHIP': 'INTERNSHIP',
                'CD LAB': 'CD Lab',
                'ES LAB': 'ES Lab',
                'DATA MINING LAB': 'Data Mining Lab',
                'OS LAB': 'OS Lab',
                'IOT LAB': 'IoT Lab',
                'JAVA LAB': 'Java Lab',
                'JAVA': 'OOPJ',
                'OOPJ': 'OOPJ',
                'CM LAB': 'CM Lab',
                'POWER BI LAB': 'DV Lab',
                'POWERBI LAB': 'DV Lab',
                'SDC LAB': 'NODE JS Lab',
                'NODE JS LAB': 'NODE JS Lab',
                'NODEJS LAB': 'NODE JS Lab',
                'FLUTTER LAB': 'Flutter Lab',
                'PROJECT STAGE I': 'Project Stage-1 Lab',
                'PROJECT STAGE - I': 'Project Stage-1 Lab',
                'PROJECT STAGE – I': 'Project Stage-1 Lab',
                'PROJECT STAGE 1': 'Project Stage-1 Lab',
                'PROJECT STAGE-1 LAB': 'Project Stage-1 Lab',
                'PROJECT STAGE 1 LAB': 'Project Stage-1 Lab',
                'COA': 'COA',
                'DV': 'DV',
                'DV LAB': 'DV Lab',
                'MOBILE COMPUTING': 'MC',
                'NATURE INSPIRED COMPUTING': 'NIC',
                'PROFESSIONAL PRACTICE, LAW & ETHICS': 'PPLE',
                'PROFESSIONAL PRACTICE LAW & ETHICS': 'PPLE',
                'PROFESSIONAL PRACTICE, LAW AND ETHICS': 'PPLE',
                'PROFESSIONAL PRACTICE LAW AND ETHICS': 'PPLE'
            };
            const normalizedTrimmedName = normalizeSubjectNameForSchedule(trimmedName);
            if (canonicalShortLabels[normalizedTrimmedName]) {
                return canonicalShortLabels[normalizedTrimmedName];
            }
            if (/^[A-Z0-9]{2,6}(?:\s+Lab)?$/.test(trimmedName)) {
                return trimmedName;
            }

            const labels = getScheduleLabelsForSubjectName(trimmedName).filter(function (label) {
                return label && label !== trimmedName;
            });
            if (isLaboratorySubject(trimmedName)) {
                const laboratoryLabel = labels.find(function (label) {
                    return isLaboratorySubject(label);
                });
                if (laboratoryLabel) {
                    return laboratoryLabel;
                }
                const fallbackLabLabel = labels[0] || buildSubjectAcronym(trimmedName) || trimmedName;
                return isLaboratorySubject(fallbackLabLabel) ? fallbackLabLabel : fallbackLabLabel + ' Lab';
            }
            return labels[0] || buildSubjectAcronym(trimmedName) || trimmedName;
        }

        function buildSubjectAcronym(subjectName) {
            const originalName = String(subjectName || '').trim();
            if (!originalName) {
                return '';
            }

            const isLab = isLaboratorySubject(originalName);
            const cleanedName = normalizeSubjectNameForSchedule(originalName)
                .replace(/\([^)]*\)/g, ' ')
                .replace(/\bLABORATORY\b|\bLAB\b/g, ' ')
                .replace(/[^A-Z0-9 ]/g, ' ')
                .replace(/\s+/g, ' ')
                .trim();
            const words = cleanedName.split(' ').filter(function (word) {
                return Boolean(word);
            });
            const acronym = words.map(function (word) {
                return word.charAt(0);
            }).join('').slice(0, 6);

            if (!acronym) {
                return isLab ? 'Lab' : originalName;
            }

            return isLab ? acronym + ' Lab' : acronym;
        }

        function resetClassTimeTableMerges(slots) {
            (slots || timeTableSlots).forEach(function (slot) {
                const cell = slot.closest('td');
                if (!cell) {
                    return;
                }
                cell.colSpan = 1;
                cell.style.display = '';
                cell.classList.remove('lab-merged-cell');
                slot.classList.remove('lab-merged-slot');
            });
        }

        function mergeSlotWithNextPeriod(slot, subjectName, slotSelector) {
            const cell = slot.closest('td');
            const row = cell ? cell.closest('tr') : null;
            const nextSlotSelector = slotSelector || (slot.classList.contains('empty-timetable-slot') ? '.empty-timetable-slot' : '.timetable-slot');
            if (!cell || !row) {
                return false;
            }

            const cells = Array.from(row.children);
            const currentIndex = cells.indexOf(cell);
            const nextCell = cells[currentIndex + 1];
            if (!nextCell || nextCell.classList.contains('break-slot') || nextCell.style.display === 'none') {
                return false;
            }

            const nextSlot = nextCell.querySelector(nextSlotSelector);
            if (!nextSlot) {
                return false;
            }

            slot.value = subjectName;
            nextSlot.value = '';
            cell.colSpan = 2;
            cell.classList.add('lab-merged-cell');
            slot.classList.add('lab-merged-slot');
            nextCell.style.display = 'none';
            return true;
        }

        function restoreClassLabMergesFromValues(slots) {
            const targetSlots = slots || timeTableSlots;
            const slotSelector = targetSlots.some(function (slot) { return slot.classList.contains('empty-timetable-slot'); })
                ? '.empty-timetable-slot'
                : '.timetable-slot';
            targetSlots.forEach(function (slot) {
                const subjectName = (slot.value || '').trim();
                if (!subjectName || !isLaboratoryScheduleValue(subjectName)) {
                    return;
                }

                const currentCell = getTimeTableSlotCell(slot);
                if (currentCell && currentCell.colSpan > 1) {
                    return;
                }
                const periodIndex = getSlotPeriodIndex(slot);
                if (periodIndex < 0 || periodIndex + 1 >= periodOrder.length) {
                    return;
                }

                const nextSlot = getClassSlot(slot.dataset.day, periodOrder[periodIndex + 1], targetSlots);
                const nextCell = getTimeTableSlotCell(nextSlot);
                if (!nextSlot || !nextCell || nextCell.style.display === 'none') {
                    return;
                }

                if (nextSlot.value.trim() && !isLaboratoryScheduleValue(nextSlot.value)) {
                    const displacedValue = nextSlot.value.trim();
                    const ignoredSlots = new Set([slot, nextSlot]);
                    const replacementSlot = targetSlots.find(function (candidate) {
                        const candidateCell = getTimeTableSlotCell(candidate);
                        return candidate !== slot && candidate !== nextSlot &&
                            candidate.dataset.day !== slot.dataset.day &&
                            normalizeClassValue(candidate.dataset.day) !== 'SAT' &&
                            candidateCell && candidateCell.style.display !== 'none' &&
                            !candidate.value.trim() &&
                            canMoveSubjectToClassSlot(targetSlots, candidate, displacedValue, 1, ignoredSlots);
                    });
                    if (!replacementSlot) {
                        return;
                    }
                    replacementSlot.value = displacedValue;
                    nextSlot.value = '';
                }

                if (nextSlot.value.trim() && isLaboratoryScheduleValue(nextSlot.value)) {
                    // Lab blocks cannot overlap. Leave this block intact and let the next
                    // adjacent empty block be considered by subsequent lab slots.
                    return;
                }

                mergeSlotWithNextPeriod(slot, subjectName, slotSelector);
            });
        }

        function getClassSlot(day, period, slots) {
            return (slots || timeTableSlots).find(function (slot) {
                return slot.dataset.day === day && slot.dataset.period === period;
            }) || null;
        }

        function isFirstSemesterTwoToFourContext(context) {
            const year = normalizeAcademicLevelValue(context && context.year);
            return ['2', '3', '4'].includes(year) &&
                normalizeAcademicLevelValue(context && context.semester) === '2';
        }

        function isR25TwoOneAIMLContext(context) {
            return Boolean(context) &&
                normalizeClassValue(context.regulation || 'R22') === 'R25' &&
                normalizeAcademicLevelValue(context.year) === '2' &&
                normalizeAcademicLevelValue(context.semester) === '1' &&
                normalizeClassValue(context.branch) === 'AIML';
        }

        function contextHasSubjectLabel(context, label) {
            const labelKey = normalizeSubjectNameForSchedule(label);
            return (context && context.slots ? context.slots : []).some(function (slot) {
                return isVisibleFilledClassSlot(slot) &&
                    normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) === labelKey;
            });
        }

        function ensureR25TwoOneAIMLOSLab(context) {
            if (!isR25TwoOneAIMLContext(context) || contextHasSubjectLabel(context, 'OS Lab')) {
                return 0;
            }

            const selections = getSelectionsForClassContext(getStoredSubjectSelections(), context);
            const assignments = buildClassAssignments(selections, context);
            const osLabAssignment = findClassAssignmentByLabel(assignments, 'OS Lab') || {
                displayName: 'OS Lab',
                subjectName: 'OS Lab',
                labRoomNumber: getStandardLabRoomNumber('OS Lab'),
                isLab: true
            };
            const osLabDisplayName = getAssignmentSlotDisplayName(osLabAssignment) || 'OS Lab';
            const preferredReplacementLabs = new Set(['CM LAB', 'DV LAB', 'SE LAB', 'DBMS LAB', 'JAVA LAB']);
            resetClassTimeTableMerges(context.slots);

            const targetSlot = (context.slots || []).find(function (slot) {
                const cell = getTimeTableSlotCell(slot);
                const periodIndex = getSlotPeriodIndex(slot);
                const valueKey = normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value));
                return cell &&
                    cell.style.display !== 'none' &&
                    slot.value.trim() &&
                    isLaboratorySubject(slot.value) &&
                    preferredReplacementLabs.has(valueKey) &&
                    [0, 3].includes(periodIndex) &&
                    normalizeClassValue(slot.dataset.day || '') !== 'SAT';
            }) || (context.slots || []).find(function (slot) {
                const cell = getTimeTableSlotCell(slot);
                const periodIndex = getSlotPeriodIndex(slot);
                const nextSlot = getClassSlot(slot.dataset.day, periodOrder[periodIndex + 1], context.slots);
                const nextCell = getTimeTableSlotCell(nextSlot);
                return cell &&
                    nextSlot &&
                    nextCell &&
                    cell.style.display !== 'none' &&
                    nextCell.style.display !== 'none' &&
                    !slot.value.trim() &&
                    !nextSlot.value.trim() &&
                    [0, 3].includes(periodIndex) &&
                    normalizeClassValue(slot.dataset.day || '') !== 'SAT';
            });

            if (!targetSlot) {
                restoreClassLabMergesFromValues(context.slots);
                return 0;
            }

            if (!mergeSlotWithNextPeriod(targetSlot, osLabDisplayName, context.slotSelector)) {
                targetSlot.value = osLabDisplayName;
                restoreClassLabMergesFromValues(context.slots);
            }
            return 1;
        }

        function ensureR25TwoOneAIMLOSLabel(classContexts) {
            return (classContexts || getClassTimeTableContexts()).reduce(function (total, context) {
                return total + ensureR25TwoOneAIMLOSLab(context);
            }, 0);
        }

        function isFourthYearFirstSemProjectContext(context) {
            const branch = normalizeClassValue(context && context.branch);
            return Boolean(context) &&
                normalizeAcademicLevelValue(context.year) === '4' &&
                normalizeAcademicLevelValue(context.semester) === '1' &&
                ['IT', 'AIML'].includes(branch);
        }

        function ensureFourthYearProjectStageLab(context) {
            if (!isFourthYearFirstSemProjectContext(context) || contextHasSubjectLabel(context, 'Project Stage-1 Lab')) {
                return 0;
            }

            const selections = getSelectionsForClassContext(getStoredSubjectSelections(), context);
            const assignments = buildClassAssignments(selections, context);
            const projectAssignment = findClassAssignmentByLabel(assignments, 'Project Stage-1 Lab') || {
                displayName: 'Project Stage-1 Lab',
                subjectName: 'Project Stage-1 Lab',
                labRoomNumber: getStandardLabRoomNumber('Project Stage-1 Lab'),
                isLab: true
            };
            const projectDisplayName = getAssignmentSlotDisplayName(projectAssignment) || 'Project Stage-1 Lab';

            resetClassTimeTableMerges(context.slots);
            const targetSlot = (context.slots || []).find(function (slot) {
                const cell = getTimeTableSlotCell(slot);
                const periodIndex = getSlotPeriodIndex(slot);
                const valueKey = normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value));
                return cell &&
                    cell.style.display !== 'none' &&
                    slot.value.trim() &&
                    isLaboratorySubject(slot.value) &&
                    valueKey !== 'PROJECT STAGE-1 LAB' &&
                    [0, 3].includes(periodIndex) &&
                    normalizeClassValue(slot.dataset.day || '') !== 'SAT';
            }) || (context.slots || []).find(function (slot) {
                const cell = getTimeTableSlotCell(slot);
                const periodIndex = getSlotPeriodIndex(slot);
                const nextSlot = getClassSlot(slot.dataset.day, periodOrder[periodIndex + 1], context.slots);
                const nextCell = getTimeTableSlotCell(nextSlot);
                return cell &&
                    nextSlot &&
                    nextCell &&
                    cell.style.display !== 'none' &&
                    nextCell.style.display !== 'none' &&
                    !slot.value.trim() &&
                    !nextSlot.value.trim() &&
                    [0, 3].includes(periodIndex) &&
                    normalizeClassValue(slot.dataset.day || '') !== 'SAT';
            });

            if (!targetSlot) {
                restoreClassLabMergesFromValues(context.slots);
                return 0;
            }

            if (!mergeSlotWithNextPeriod(targetSlot, projectDisplayName, context.slotSelector)) {
                targetSlot.value = projectDisplayName;
                restoreClassLabMergesFromValues(context.slots);
            }
            return 1;
        }

        function ensureFourthYearProjectStageLabs(classContexts) {
            return 0;
        }

        const timetableActivityLabels = ['MENTORING', 'SPORTS', 'LIBRARY', 'EVS/IKS', 'VEGS'];
        const timetableActivityOrder = new Map(timetableActivityLabels.map(function (label, index) {
            return [label, index];
        }));

        function getTimetableActivityKey(value) {
            const key = normalizeSubjectNameForSchedule(getComparableSubjectValue(value));
            return timetableActivityOrder.has(key) ? key : '';
        }

        // SPORTS block length depends on the academic level:
        //  - 2-2 (II-II) timetables: a single 2-hour merged block;
        //  - 3-2 (III-II) and every other level: a single 1-hour block.
        function getSportsDurationForContext(context) {
            if (isR25TwoTwoITContext(context)) {
                return 1;
            }
            const year = normalizeAcademicLevelValue(
                (context && (context.year || (context.meta && context.meta.year) || (context.context && context.context.year))) || ''
            );
            return year === '2' ? 2 : 1;
        }

        // Normalise the SPORTS hours in a context so they match the required block length
        // for the academic level (2 hours merged for 2-1, 1 hour for 3-1).
        function ensureSportsBlock(context) {
            if (!context || !context.slots) {
                return 0;
            }
            const slots = context.slots;
            const targetHours = getSportsDurationForContext(context);
            const days = Array.from(new Set(slots.map(function (slot) {
                return slot.dataset.day || '';
            }).filter(Boolean)));
            let changes = 0;
            days.forEach(function (day) {
                const sportsSlots = slots.filter(function (slot) {
                    const cell = getTimeTableSlotCell(slot);
                    return cell && cell.style.display !== 'none' && slot.dataset.day === day &&
                        normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) === 'SPORTS';
                });
                let sportsCount = sportsSlots.reduce(function (total, slot) {
                    const cell = getTimeTableSlotCell(slot);
                    return total + ((cell.colSpan && cell.colSpan > 1) ? 2 : 1);
                }, 0);
                if (sportsCount > targetHours) {
                    let remaining = sportsCount - targetHours;
                    sportsSlots.forEach(function (slot) {
                        if (remaining <= 0) {
                            return;
                        }
                        const cell = getTimeTableSlotCell(slot);
                        if (cell && cell.colSpan > 1) {
                            restoreClassLabMergesFromValues(slots);
                        }
                        slot.value = '';
                        remaining -= (cell && cell.colSpan > 1) ? 2 : 1;
                        changes += 1;
                    });
                }
                if (targetHours >= 2) {
                    const sportsCells = slots.filter(function (slot) {
                        const cell = getTimeTableSlotCell(slot);
                        return cell && cell.style.display !== 'none' && slot.dataset.day === day &&
                            normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) === 'SPORTS';
                    }).sort(function (a, b) {
                        return periodOrder.indexOf(a.dataset.period) - periodOrder.indexOf(b.dataset.period);
                    });
                    const allSingle = sportsCells.length === 2 && sportsCells.every(function (slot) {
                        const cell = getTimeTableSlotCell(slot);
                        return !(cell.colSpan && cell.colSpan > 1);
                    });
                    if (allSingle) {
                        const firstSlot = sportsCells[0];
                        const firstIndex = periodOrder.indexOf(firstSlot.dataset.period);
                        const nextSlot = getClassSlot(day, periodOrder[firstIndex + 1], slots);
                        const nextCell = nextSlot ? getTimeTableSlotCell(nextSlot) : null;
                        if (nextSlot && nextCell && nextCell.style.display !== 'none' && !nextSlot.value.trim()) {
                            mergeSlotWithNextPeriod(firstSlot, 'SPORTS', context.slotSelector);
                            changes += 1;
                        }
                    }
                }
            });
            return changes;
        }

        function enforceActivitiesLastHoursForContext(context) {
            if (!context || !isFirstSemesterTwoToFourContext(context)) {
                return 0;
            }

            const slots = context.slots || [];
            const days = Array.from(new Set(slots.map(function (slot) {
                return slot.dataset.day || '';
            }).filter(Boolean)));
            const lastPeriod = periodOrder[periodOrder.length - 1];
            const preferredActivityDays = {
                MENTORING: 'THU',
                SPORTS: 'FRI',
                LIBRARY: 'SAT'
            };
            const preferredDayOrder = ['THU', 'FRI', 'SAT', 'MON', 'TUE', 'WED'];
            let changes = 0;

            resetClassTimeTableMerges(slots);

            const visibleSlots = slots.filter(function (slot) {
                const cell = getTimeTableSlotCell(slot);
                return slot && cell && cell.style.display !== 'none';
            });
            const activityEntriesByKey = new Map();
            const duplicateActivitySlots = [];
            visibleSlots.forEach(function (slot) {
                const activityKey = getTimetableActivityKey(slot.value);
                if (!activityKey) {
                    return;
                }
                if (activityEntriesByKey.has(activityKey)) {
                    duplicateActivitySlots.push(slot);
                    return;
                }
                activityEntriesByKey.set(activityKey, {
                    key: activityKey,
                    slot: slot,
                    value: normalizeTimeTableDisplayValue(activityKey)
                });
            });

            const lastSlotsByDay = new Map();
            days.forEach(function (day) {
                const slot = getClassSlot(day, lastPeriod, slots);
                const cell = getTimeTableSlotCell(slot);
                if (slot && cell && cell.style.display !== 'none') {
                    lastSlotsByDay.set(day, slot);
                }
            });

            // For semester-II cohorts, enforce only the requested weekly hours.
            const activityEntries = ['SPORTS', 'LIBRARY'].map(function (label) {
                return activityEntriesByKey.get(label) || {
                    key: label,
                    slot: null,
                    value: normalizeTimeTableDisplayValue(label),
                    missing: true
                };
            });
            if (!activityEntries.length || !lastSlotsByDay.size) {
                restoreClassLabMergesFromValues(slots);
                return 0;
            }

            const usedTargetSlots = new Set();
            const assignments = activityEntries.map(function (entry) {
                const preferredDay = preferredActivityDays[entry.key];
                let targetSlot = preferredDay ? lastSlotsByDay.get(preferredDay) : null;
                if ((!targetSlot || usedTargetSlots.has(targetSlot)) && entry.slot) {
                    targetSlot = lastSlotsByDay.get(entry.slot.dataset.day || '');
                }
                if (!targetSlot || usedTargetSlots.has(targetSlot)) {
                    targetSlot = preferredDayOrder.map(function (day) {
                        return lastSlotsByDay.get(day);
                    }).concat(Array.from(lastSlotsByDay.values())).find(function (candidate) {
                        return candidate && !usedTargetSlots.has(candidate);
                    }) || null;
                }
                if (targetSlot) {
                    usedTargetSlots.add(targetSlot);
                }
                return {
                    entry: entry,
                    targetSlot: targetSlot
                };
            }).filter(function (assignment) {
                return Boolean(assignment.targetSlot);
            });

            const sourceSlots = new Set(activityEntries.map(function (entry) {
                return entry.slot;
            }).filter(Boolean).concat(duplicateActivitySlots));
            const targetSlots = new Set(assignments.map(function (assignment) {
                return assignment.targetSlot;
            }));
            const nonTargetSourceSlots = activityEntries.map(function (entry) {
                return entry.slot;
            }).filter(function (slot) {
                return slot && !targetSlots.has(slot);
            });
            const relocationSlots = visibleSlots.filter(function (slot) {
                return !sourceSlots.has(slot) && !targetSlots.has(slot) && !slot.value.trim();
            });

            const displacedValues = [];
            assignments.forEach(function (assignment) {
                if (sourceSlots.has(assignment.targetSlot) || !assignment.targetSlot.value.trim()) {
                    return;
                }
                if (assignment.entry.slot) {
                    displacedValues.push(assignment.targetSlot.value);
                    return;
                }
                const relocationSlot = relocationSlots.shift();
                if (relocationSlot) {
                    relocationSlot.value = assignment.targetSlot.value;
                    changes += 1;
                    return;
                }
                assignment.skip = true;
            });

            const activeAssignments = assignments.filter(function (assignment) {
                return !assignment.skip;
            });
            const activeTargetSlots = new Set(activeAssignments.map(function (assignment) {
                return assignment.targetSlot;
            }));

            activeAssignments.forEach(function (assignment) {
                if (assignment.targetSlot.value !== assignment.entry.value) {
                    assignment.targetSlot.value = assignment.entry.value;
                    changes += 1;
                }
            });

            nonTargetSourceSlots.forEach(function (slot, index) {
                const replacement = displacedValues[index] || '';
                if (slot.value !== replacement) {
                    slot.value = replacement;
                    changes += 1;
                }
            });

            duplicateActivitySlots.forEach(function (slot) {
                if (!activeTargetSlots.has(slot) && slot.value) {
                    slot.value = '';
                    changes += 1;
                }
            });

            restoreClassLabMergesFromValues(slots);
            return changes;
        }

        function enforceActivitiesLastHours(classContexts) {
            return (classContexts || getClassTimeTableContexts()).reduce(function (total, context) {
                return total + enforceActivitiesLastHoursForContext(context);
            }, 0);
        }

        function getVisibleEmptyClassSlots() {
            return timeTableSlots.filter(function (slot) {
                const cell = slot.closest('td');
                return cell && cell.style.display !== 'none' && !slot.value.trim();
            });
        }

        function setSlotIfEmpty(slot, value) {
            if (!slot || slot.value.trim()) {
                return false;
            }
            slot.value = value;
            return true;
        }

        function applyLaboratoryBlocks(subjectNames) {
            const laboratorySubjects = Array.from(new Set((subjectNames || []).filter(isLaboratorySubject)));
            if (!laboratorySubjects.length) {
                return 0;
            }

            const preferredStartPeriods = ['9:30-10:30', '1:20-2:15']; // Merge hours 1+2 and 4+5 only.
            const days = Array.from(new Set(timeTableSlots.map(function (slot) {
                return slot.dataset.day || '';
            }).filter(Boolean)));
            let mergedCount = 0;

            laboratorySubjects.forEach(function (subjectName, subjectIndex) {
                for (let dayOffset = 0; dayOffset < days.length; dayOffset += 1) {
                    const day = days[(subjectIndex + dayOffset) % days.length];
                    for (let periodIndex = 0; periodIndex < preferredStartPeriods.length; periodIndex += 1) {
                        const slot = timeTableSlots.find(function (candidate) {
                            return candidate.dataset.day === day && candidate.dataset.period === preferredStartPeriods[periodIndex];
                        });

                        if (slot && mergeSlotWithNextPeriod(slot, subjectName)) {
                            mergedCount += 1;
                            return;
                        }
                    }
                }
            });

            return mergedCount;
        }

        function generateIndividualTimeTableSlots(subjectNames, preferredHours, card) {
            const subjects = (subjectNames || []).filter(Boolean);
            const slots = getIndividualTimeTableSlots(card);
            const hourLimit = Math.min(Math.max(preferredHours || 16, 14), 16, slots.length);
            const filledHours = subjects.length ? hourLimit : 0;

            slots.forEach(function (slot) {
                slot.value = '';
            });

            for (let index = 0; index < filledHours; index += 1) {
                slots[index].value = subjects[index % subjects.length];
            }

            return filledHours;
        }

        function buildIndividualFacultySchedules(selections) {
            const facultyMap = new Map();
            normalizeSubjectSelections(selections).forEach(function (selection) {
                const facultyName = (selection.facultyName || '').trim();
                const employeeCode = (selection.employeeCode || '').trim();
                const employeeCodeKey = normalizeClassValue(employeeCode).replace(/[^A-Z0-9]/g, '');
                const subjectName = (selection.subjectName || '').trim();
                const subjectLabels = getScheduleLabelsForSelection(selection);
                const normalizedFacultyKey = normalizeSubjectNameForSchedule(facultyName).replace(/[^A-Z0-9]/g, '');
                const key = employeeCodeKey || normalizedFacultyKey || 'faculty-' + facultyMap.size;

                if (!facultyMap.has(key)) {
                    facultyMap.set(key, {
                        facultyName: facultyName,
                        employeeCode: employeeCode,
                        subjects: [],
                        subjectLabels: [],
                        selections: []
                    });
                }

                const schedule = facultyMap.get(key);
                if (facultyName && !schedule.facultyName) {
                    schedule.facultyName = facultyName;
                }
                if (employeeCode && !schedule.employeeCode) {
                    schedule.employeeCode = employeeCode;
                }

                if (subjectName && !schedule.subjects.includes(subjectName)) {
                    schedule.subjects.push(subjectName);
                }
                schedule.selections.push(selection);
                subjectLabels.forEach(function (label) {
                    if (label && !schedule.subjectLabels.includes(label)) {
                        schedule.subjectLabels.push(label);
                    }
                });
            });

            return Array.from(facultyMap.values()).filter(function (schedule) {
                return schedule.facultyName || schedule.employeeCode || schedule.subjects.length;
            });
        }

        function getFacultyScheduleKey(selection) {
            const employeeCode = normalizeClassValue(selection.employeeCode || '').replace(/[^A-Z0-9]/g, '');
            const facultyName = normalizeSubjectNameForSchedule(selection.facultyName || '').replace(/[^A-Z0-9]/g, '');
            return employeeCode || facultyName || '';
        }

        function getClassContextKey(year, semester, branch) {
            return [
                normalizeClassValue(year),
                normalizeClassValue(semester),
                normalizeBranchValue(branch)
            ].join('-');
        }

        function shouldUseSectionContext(branch) {
            const normalizedBranch = normalizeClassValue(branch);
            return normalizedBranch === 'AIML' || normalizedBranch === 'CSE(AI&ML)';
        }

        function getSectionContextValue(section, branch) {
            return shouldUseSectionContext(branch) ? normalizeClassValue(section || 'A') : '';
        }

        const allowedGeneratedClassContexts = [
            { regulation: 'R25', year: '2', semester: '1', branch: 'AIML', section: 'A' },
            { regulation: 'R25', year: '2', semester: '1', branch: 'AIML', section: 'B' },
            { regulation: 'R25', year: '2', semester: '1', branch: 'IT', section: '' },
            { regulation: 'R25', year: '2', semester: '2', branch: 'AIML', section: 'A' },
            { regulation: 'R25', year: '2', semester: '2', branch: 'AIML', section: 'B' },
            { regulation: 'R25', year: '2', semester: '2', branch: 'IT', section: '' },
            { regulation: 'R22', year: '3', semester: '1', branch: 'AIML', section: 'A' },
            { regulation: 'R22', year: '3', semester: '1', branch: 'AIML', section: 'B' },
            { regulation: 'R22', year: '3', semester: '1', branch: 'IT', section: '' },
            { regulation: 'R22', year: '3', semester: '2', branch: 'AIML', section: 'A' },
            { regulation: 'R22', year: '3', semester: '2', branch: 'AIML', section: 'B' },
            { regulation: 'R22', year: '3', semester: '2', branch: 'IT', section: '' },
            { regulation: 'R22', year: '4', semester: '1', branch: 'AIML', section: 'A' },
            { regulation: 'R22', year: '4', semester: '1', branch: 'AIML', section: 'B' },
            { regulation: 'R22', year: '4', semester: '1', branch: 'IT', section: '' },
            { regulation: 'R22', year: '4', semester: '2', branch: 'AIML', section: 'A' },
            { regulation: 'R22', year: '4', semester: '2', branch: 'AIML', section: 'B' },
            { regulation: 'R22', year: '4', semester: '2', branch: 'IT', section: '' }
        ];

        function getAllowedGeneratedClassContextSpec(regulation, year, semester, branch, section) {
            const normalizedRegulation = normalizeClassValue(regulation || 'R22');
            const normalizedYear = normalizeAcademicLevelValue(year);
            const normalizedSemester = normalizeAcademicLevelValue(semester);
            const normalizedBranch = normalizeBranchValue(branch);
            const normalizedSection = getSectionContextValue(section, normalizedBranch);
            return allowedGeneratedClassContexts.find(function (spec) {
                return spec.regulation === normalizedRegulation &&
                    spec.year === normalizedYear &&
                    spec.semester === normalizedSemester &&
                    spec.branch === normalizedBranch &&
                    spec.section === normalizedSection;
            }) || null;
        }

        function isAllowedGeneratedClassContext(context) {
            return Boolean(context && getAllowedGeneratedClassContextSpec(
                context.regulation,
                context.year,
                context.semester,
                context.branch,
                context.section
            ));
        }

        function requiresMorningTheoryCoverage(context) {
            if (!context) {
                return false;
            }
            const regulation = normalizeClassValue(context.regulation || 'R22');
            const year = normalizeAcademicLevelValue(context.year);
            const semester = normalizeAcademicLevelValue(context.semester);
            return (regulation === 'R25' && year === '2' && semester === '2') ||
                (regulation === 'R22' && ((year === '3' && semester === '2') || (year === '4' && semester === '2')));
        }

        function repairMorningTheoryCoverage(contexts, selections) {
            let repaired = 0;
            const normalizedSelections = normalizeSubjectSelections(selections || []);
            (contexts || []).forEach(function (context) {
                if (!requiresMorningTheoryCoverage(context)) {
                    return;
                }
                const contextSelections = getSelectionsForClassContext(normalizedSelections, context);
                const assignments = buildClassAssignments(contextSelections, context).filter(function (assignment) {
                    return !assignment.isLab && !assignment.isActivity &&
                        normalizeSubjectNameForSchedule(assignment.displayName || assignment.subjectName) !== 'SPORTS' &&
                        (assignment.targetHours || 0) > 0;
                });
                assignments.forEach(function (assignment) {
                    const subjectKey = getAssignmentSubjectKey(assignment);
                    const slots = context.slots || [];
                    const hasMorningSlot = slots.some(function (slot) {
                        return slot.dataset.period === periodOrder[0] && isVisibleFilledClassSlot(slot) &&
                            normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) === subjectKey;
                    });
                    if (hasMorningSlot) {
                        return;
                    }

                    const occurrences = slots.filter(function (slot) {
                        const cell = getTimeTableSlotCell(slot);
                        return isVisibleFilledClassSlot(slot) && getSlotPeriodIndex(slot) > 0 &&
                            (!cell || cell.colSpan <= 1) &&
                            normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) === subjectKey;
                    });
                    if (!occurrences.length) {
                        return;
                    }

                    let moved = false;
                    const days = Array.from(new Set(slots.map(function (slot) {
                        return slot.dataset.day || '';
                    }).filter(Boolean)));
                    days.some(function (day) {
                        const target = getClassSlot(day, periodOrder[0], slots);
                        if (!target || !target.closest('td') || target.closest('td').style.display === 'none' || target.value.trim()) {
                            return false;
                        }
                        return occurrences.some(function (source) {
                            const duplicateRemainsOnTargetDay = slots.some(function (slot) {
                                return slot !== source && slot.dataset.day === day && isVisibleFilledClassSlot(slot) &&
                                    normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) === subjectKey;
                            });
                            if (duplicateRemainsOnTargetDay) {
                                return false;
                            }
                            const facultyOccupancyMap = createFacultyOccupancyMap();
                            const labRoomOccupancyMap = createLabRoomOccupancyMap();
                            prePopulateOccupancyMapsFromExistingData(facultyOccupancyMap, labRoomOccupancyMap);
                            if (!canUseClassSlot(context, day, 0, 1, assignment.facultyKey, facultyOccupancyMap, false, assignment, null, labRoomOccupancyMap)) {
                                return false;
                            }
                            target.value = source.value;
                            source.value = '';
                            repaired += 1;
                            moved = true;
                            return true;
                        });
                    });
                    if (!moved) {
                        console.warn('Could not place a 9:30-10:30 theory hour for', assignment.displayName || assignment.subjectName, context.label || 'timetable');
                    }
                });
            });
            return repaired;
        }

        function getSelectionContextKey(selection) {
            const branch = normalizeBranchValue(selection.branch);
            return [
                normalizeClassValue(selection.regulation || 'R22'),
                getClassContextKey(selection.year, selection.semester, branch),
                getSectionContextValue(selection.section, branch)
            ].filter(function (entry) {
                return entry !== '';
            }).join('|');
        }

        function normalizeAcademicLevelValue(value) {
            const romanMap = { I: '1', II: '2', III: '3', IV: '4' };
            const normalizedValue = normalizeClassValue(value);
            return romanMap[normalizedValue] || normalizedValue;
        }

        function normalizeBranchValue(value) {
            const normalized = normalizeClassValue(value || '');
            if (normalized === 'CSE(AI&ML)' || normalized === 'CSE(AI/ML)') {
                return 'AIML';
            }
            return normalized;
        }

        function getClassKeyFromSelection(selection) {
            return getClassContextKey(selection.year, selection.semester, normalizeBranchValue(selection.branch));
        }

        function getBranchDisplayLabel(branch) {
            const normalizedBranch = normalizeClassValue(branch);
            if (normalizedBranch === 'AIML') {
                return 'CSE (AI&ML)';
            }
            if (normalizedBranch === 'H&S') {
                return 'H & S';
            }
            return branch || 'IT';
        }

        function getYearSemLabel(year, semester) {
            const romanYears = { 1: 'I', 2: 'II', 3: 'III', 4: 'IV' };
            const romanSemesters = { 1: 'I', 2: 'II' };
            return (romanYears[Number(year)] || year || 'III') + '-' + (romanSemesters[Number(semester)] || semester || 'I');
        }

        function getClassContextLabel(regulation, year, semester, branch, section) {
            const sectionLabel = getSectionContextValue(section, branch);
            return [
                regulation || 'R22',
                getYearSemLabel(year, semester),
                getBranchDisplayLabel(branch),
                sectionLabel ? 'Section ' + sectionLabel : ''
            ].filter(Boolean).join(' ');
        }

        function choosePrimarySubjectSelection(selections) {
            const normalizedSelections = normalizeSubjectSelections(selections);
            const preferredSelection = normalizedSelections.find(function (selection) {
                return Boolean(getAllowedGeneratedClassContextSpec(
                    selection.regulation,
                    selection.year,
                    selection.semester,
                    selection.branch,
                    selection.section
                ));
            });
            if (preferredSelection) {
                return preferredSelection;
            }
            return normalizedSelections.find(function (selection) {
                return normalizeClassValue(selection.year) === '3' &&
                    normalizeClassValue(selection.semester) === '1';
            }) || normalizedSelections[0] || null;
        }

        function findSelectionForClass(selections, year, semester, branch, regulation, section) {
            const classKey = getClassContextKey(year, semester, normalizeBranchValue(branch));
            const normalizedRegulation = regulation ? normalizeClassValue(regulation) : '';
            const normalizedSection = getSectionContextValue(section, normalizeBranchValue(branch));
            return normalizeSubjectSelections(selections).find(function (selection) {
                return getClassKeyFromSelection(selection) === classKey &&
                    (!normalizedRegulation || normalizeClassValue(selection.regulation || 'R22') === normalizedRegulation) &&
                    getSectionContextValue(selection.section, normalizeBranchValue(selection.branch)) === normalizedSection;
            }) || normalizeSubjectSelections(selections).find(function (selection) {
                return getClassKeyFromSelection(selection) === classKey &&
                    (!normalizedRegulation || normalizeClassValue(selection.regulation || 'R22') === normalizedRegulation);
            }) || null;
        }

        function getContextRegulation(selection) {
            return normalizeClassValue(selection && selection.regulation ? selection.regulation : (subjectSelectionFields.regulation ? subjectSelectionFields.regulation.value : 'R22'));
        }

        function updateClassContextTitle(context) {
            if (!context || !context.titleElement) {
                return;
            }
            context.titleElement.textContent = context.label + ' Time Table';
            const container = context.titleElement.closest('[data-empty-timetable-card]') || document.getElementById('timetable');
            const downloadButton = container ? container.querySelector('[data-download-main-timetable]') : null;
            if (downloadButton) {
                downloadButton.dataset.tableTitle = context.label + ' Time Table';
            }
        }

        function getClassTimeTableContexts(selections) {
            const contexts = [];
            const seen = new Set();
            const primarySpec = primaryFixedTimeTableSpec;
            const primaryYear = primarySpec.year;
            const primarySemester = primarySpec.semester;
            const primaryBranch = primarySpec.branch;
            const primaryRegulation = primarySpec.regulation;
            const primarySection = primarySpec.section;

            function addContext(context) {
                if (!context.selectionKey || seen.has(context.selectionKey) || !isAllowedGeneratedClassContext(context)) {
                    return false;
                }
                seen.add(context.selectionKey);
                updateClassContextTitle(context);
                contexts.push(context);
                return true;
            }

            addContext({
                key: getClassContextKey(primaryYear, primarySemester, primaryBranch),
                selectionKey: [
                    primaryRegulation,
                    getClassContextKey(primaryYear, primarySemester, primaryBranch),
                    getSectionContextValue(primarySection, primaryBranch)
                ].filter(function (entry) {
                    return entry !== '';
                }).join('|'),
                regulation: primaryRegulation,
                year: normalizeClassValue(primaryYear),
                semester: normalizeClassValue(primarySemester),
                branch: normalizeClassValue(primaryBranch),
                section: getSectionContextValue(primarySection, primaryBranch),
                label: getClassContextLabel(primaryRegulation, primaryYear, primarySemester, primaryBranch, primarySection),
                slots: timeTableSlots,
                slotSelector: '.timetable-slot',
                titleElement: document.querySelector('#timetable .section-title'),
                isPrimary: true
            });

            emptyTimeTableCards.forEach(function (card) {
                const yearSem = String(card.dataset.yearSem || '').split('-');
                const year = yearSem[0] || '';
                const semester = yearSem[1] || '';
                const branch = card.dataset.branch || 'IT';
                const cardSection = getSectionContextValue(card.dataset.section || '', branch);
                const allowedSpec = allowedGeneratedClassContexts.find(function (spec) {
                    return spec.year === normalizeAcademicLevelValue(year) &&
                        spec.semester === normalizeAcademicLevelValue(semester) &&
                        spec.branch === normalizeClassValue(branch) &&
                        (!shouldUseSectionContext(branch) || spec.section === cardSection);
                }) || null;
                if (!allowedSpec) {
                    card.style.display = 'none';
                    return;
                }
                const matchingSelection = findSelectionForClass(selections, year, semester, branch, allowedSpec.regulation, allowedSpec.section);
                const regulation = allowedSpec.regulation;
                const section = allowedSpec.section || (matchingSelection ? (matchingSelection.section || 'A') : '');
                const added = addContext({
                    key: getClassContextKey(year, semester, branch),
                    selectionKey: [
                        regulation,
                        getClassContextKey(year, semester, branch),
                        getSectionContextValue(section, branch)
                    ].filter(function (entry) {
                        return entry !== '';
                    }).join('|'),
                    regulation: regulation,
                    year: normalizeClassValue(year),
                    semester: normalizeClassValue(semester),
                    branch: normalizeClassValue(branch),
                    section: getSectionContextValue(section, branch),
                    label: getClassContextLabel(regulation, year, semester, branch, section),
                    slots: Array.from(card.querySelectorAll('.empty-timetable-slot')),
                    slotSelector: '.empty-timetable-slot',
                    titleElement: card.querySelector('.card-title'),
                    isPrimary: false
                });
                card.style.display = added ? '' : 'none';
            });

            return contexts;
        }

        function getSelectionsForClassContext(selections, context) {
            return normalizeSubjectSelections(selections).filter(function (selection) {
                return getSelectionContextKey(selection) === context.selectionKey &&
                    ((selection.subjectCode || '').trim() || (selection.subjectName || '').trim());
            });
        }

        function getSelectionsForClassContexts(selections, contexts) {
            const keys = new Set((contexts || []).map(function (context) {
                return context.selectionKey;
            }));
            return normalizeSubjectSelections(selections).filter(function (selection) {
                return keys.has(getSelectionContextKey(selection));
            });
        }

        function createFacultyOccupancyMap() {
            return new Map();
        }

        function createLabRoomOccupancyMap() {
            return new Map();
        }

        function getFacultyDayOccupancy(occupancyMap, facultyKey, day) {
            if (!occupancyMap.has(facultyKey)) {
                occupancyMap.set(facultyKey, new Map());
            }
            const facultyDays = occupancyMap.get(facultyKey);
            if (!facultyDays.has(day)) {
                facultyDays.set(day, new Set());
            }
            return facultyDays.get(day);
        }

        function canFacultyTeachWithGap(occupancyMap, facultyKey, day, startPeriodIndex, duration) {
            if (!facultyKey) {
                return true;
            }
            const occupiedPeriods = getFacultyDayOccupancy(occupancyMap, facultyKey, day);
            for (let offset = 0; offset < duration; offset += 1) {
                const candidatePeriod = startPeriodIndex + offset;
                for (const occupiedPeriod of occupiedPeriods) {
                    if (Math.abs(candidatePeriod - occupiedPeriod) <= 1) {
                        return false;
                    }
                }
            }
            return true;
        }

        function reserveFacultyPeriods(occupancyMap, facultyKey, day, startPeriodIndex, duration) {
            if (!facultyKey || !occupancyMap) {
                return;
            }
            const occupiedPeriods = getFacultyDayOccupancy(occupancyMap, facultyKey, day);
            for (let offset = 0; offset < duration; offset += 1) {
                occupiedPeriods.add(startPeriodIndex + offset);
            }
        }

        function getLabRoomKey(labRoomNumber) {
            return normalizeClassValue(labRoomNumber || '');
        }

        function getLabRoomDayOccupancy(occupancyMap, labRoomKey, day) {
            if (!occupancyMap || !labRoomKey) {
                return null;
            }
            if (!occupancyMap.has(labRoomKey)) {
                occupancyMap.set(labRoomKey, new Map());
            }
            const roomDays = occupancyMap.get(labRoomKey);
            if (!roomDays.has(day)) {
                roomDays.set(day, new Set());
            }
            return roomDays.get(day);
        }

        function hasLabRoomPeriodConflict(occupancyMap, assignment, day, startPeriodIndex, duration) {
            const labRoomKey = assignment && assignment.isLab
                ? (getLabRoomKey(assignment.labRoomNumber || getStandardLabRoomNumber(assignment.displayName || assignment.subjectName)) || 'UNASSIGNED')
                : '';
            if (!labRoomKey) {
                return false;
            }
            const occupiedPeriods = getLabRoomDayOccupancy(occupancyMap, labRoomKey, day);
            for (let offset = 0; offset < duration; offset += 1) {
                if (occupiedPeriods && occupiedPeriods.has(startPeriodIndex + offset)) {
                    return true;
                }
            }
            return false;
        }

        function reserveLabRoomPeriods(occupancyMap, assignment, day, startPeriodIndex, duration) {
            const labRoomKey = assignment && assignment.isLab
                ? (getLabRoomKey(assignment.labRoomNumber || getStandardLabRoomNumber(assignment.displayName || assignment.subjectName)) || 'UNASSIGNED')
                : '';
            if (!labRoomKey) {
                return;
            }
            const occupiedPeriods = getLabRoomDayOccupancy(occupancyMap, labRoomKey, day);
            for (let offset = 0; offset < duration; offset += 1) {
                occupiedPeriods.add(startPeriodIndex + offset);
            }
        }

        function hasLabRoomSelections(selections) {
            return normalizeSubjectSelections(selections).some(function (selection) {
                return Boolean(getLabRoomKey(selection.labRoomNumber));
            });
        }

        function getFacultyOccupancyKey(selection) {
            return getFacultyScheduleKey(selection);
        }

        function prePopulateOccupancyMapsFromExistingData(facultyOccupancyMap, labRoomOccupancyMap) {
            const allSlots = timeTableSlots.concat(getEmptyTimeTableSlots());
            allSlots.forEach(function (slot) {
                const value = (slot.value || '').trim();
                if (!value) {
                    return;
                }
                const comparableValue = getComparableSubjectValue(value);
                const subjectKey = normalizeSubjectNameForSchedule(comparableValue);
                const day = slot.dataset.day || '';
                const periodIndex = periodOrder.indexOf(slot.dataset.period || '');
                if (day && periodIndex >= 0) {
                    const isLab = isLaboratoryScheduleValue(comparableValue) || isLaboratoryScheduleValue(value);
                    const cell = getTimeTableSlotCell(slot);
                    const duration = cell && cell.colSpan > 1 ? cell.colSpan : (isLab ? 2 : 1);
                    const assignment = {
                        isLab: isLab,
                        subjectName: comparableValue,
                        displayName: comparableValue,
                        labRoomNumber: '',
                        facultyKey: ''
                    };
                    const labRoomMatch = value.match(/\((?:LAB\s*)?ROOM:\s*([^)]+)\)/i);
                    if (labRoomMatch) {
                        assignment.labRoomNumber = labRoomMatch[1].trim();
                    }
                    if (!assignment.labRoomNumber && isLab) {
                        assignment.labRoomNumber = getStandardLabRoomNumber(comparableValue);
                    }
                    if (isLab && labRoomOccupancyMap) {
                        reserveLabRoomPeriods(labRoomOccupancyMap, assignment, day, periodIndex, duration);
                    }
                }
            });
            const selections = getStoredSubjectSelections();
            const normalizedSelections = normalizeSubjectSelections(selections);
            const classContexts = getClassTimeTableContexts(normalizedSelections);
            (classContexts || []).forEach(function (context) {
                const contextSelections = getSelectionsForClassContext(normalizedSelections, context);
                const assignments = buildClassAssignments(contextSelections, context);
                (context.slots || []).forEach(function (slot) {
                    const slotValue = (slot.value || '').trim();
                    if (!slotValue) {
                        return;
                    }
                    const comparableValue = getComparableSubjectValue(slotValue);
                    const assignment = findClassAssignmentByLabel(assignments, comparableValue);
                    const day = slot.dataset.day || '';
                    const periodIndex = periodOrder.indexOf(slot.dataset.period || '');
                    const cell = getTimeTableSlotCell(slot);
                    if (!assignment || !day || periodIndex < 0) {
                        return;
                    }
                    const duration = cell && cell.colSpan > 1 ? cell.colSpan : (assignment.isLab ? 2 : 1);
                    reserveFacultyPeriods(facultyOccupancyMap, assignment.facultyKey, day, periodIndex, duration);
                    if (assignment.isLab) {
                        const roomMatch = slotValue.match(/\((?:LAB\s*)?ROOM:\s*([^)]+)\)/i);
                        const labAssignment = Object.assign({}, assignment, {
                            labRoomNumber: (roomMatch && roomMatch[1].trim()) || assignment.labRoomNumber ||
                                getStandardLabRoomNumber(assignment.displayName || assignment.subjectName)
                        });
                        reserveLabRoomPeriods(labRoomOccupancyMap, labAssignment, day, periodIndex, duration);
                    }
                });
            });
        }

        function hasFacultyConflict(occupancyMap, facultyKey, day, periodIndex, duration) {
            if (!facultyKey || !occupancyMap) {
                return false;
            }
            const occupiedPeriods = getFacultyDayOccupancy(occupancyMap, facultyKey, day);
            for (let offset = 0; offset < duration; offset += 1) {
                const candidatePeriod = periodIndex + offset;
                for (const occupiedPeriod of occupiedPeriods) {
                    if (Math.abs(candidatePeriod - occupiedPeriod) <= 1) {
                        return true;
                    }
                }
            }
            return false;
        }

        function createSubjectPeriodUsageMap() {
            return new Map();
        }

        function getAssignmentSubjectKey(assignment) {
            return normalizeSubjectNameForSchedule(assignment && (assignment.displayName || assignment.subjectName));
        }

        function hasSubjectPeriodConflict(subjectPeriodUsageMap, assignment, startPeriodIndex, duration) {
            if (!subjectPeriodUsageMap) {
                return false;
            }

            const subjectKey = getAssignmentSubjectKey(assignment);
            if (!subjectKey) {
                return false;
            }

            for (let offset = 0; offset < duration; offset += 1) {
                const usedSubjects = subjectPeriodUsageMap.get(startPeriodIndex + offset);
                if (usedSubjects && usedSubjects.has(subjectKey)) {
                    return true;
                }
            }

            return false;
        }

        function reserveSubjectPeriods(subjectPeriodUsageMap, assignment, startPeriodIndex, duration) {
            if (!subjectPeriodUsageMap) {
                return;
            }

            const subjectKey = getAssignmentSubjectKey(assignment);
            if (!subjectKey) {
                return;
            }

            for (let offset = 0; offset < duration; offset += 1) {
                const periodIndex = startPeriodIndex + offset;
                if (!subjectPeriodUsageMap.has(periodIndex)) {
                    subjectPeriodUsageMap.set(periodIndex, new Set());
                }
                subjectPeriodUsageMap.get(periodIndex).add(subjectKey);
            }
        }

        function getAssignmentSlotDisplayName(assignment) {
            if (!assignment) {
                return '';
            }
            const displayName = assignment.displayName || assignment.subjectName || '';
            const normalizedDisplayName = normalizeSubjectNameForSchedule(displayName);
            const forcedLabRoomNumber = normalizedDisplayName === 'DV LAB' || normalizedDisplayName === 'POWER BI LAB' ? 'D-417' : '';
            const labRoomNumber = assignment.isLab ? (forcedLabRoomNumber || (assignment.labRoomNumber || '').trim() || getStandardLabRoomNumber(displayName)) : '';
            return labRoomNumber ? displayName + ' (Room: ' + labRoomNumber + ')' : displayName;
        }

        function getStandardLabRoomNumber(labName) {
            const key = normalizeSubjectNameForSchedule(labName || '');
            const roomMap = {
                'FLUTTER LAB': 'E-201',
                'SDC LAB': 'E-201',
                'EMBEDDED SYSTEMS LAB': 'A-104',
                'ES LAB': 'A-104',
                'ML LAB': 'E-201',
                'CN LAB': 'E-201',
                'NLP LAB': 'E-201',
                'DA LAB': 'E-201',
                'AECS LAB': 'D-218',
                'ADVANCED ENGLISH COMMUNICATION SKILLS LAB': 'D-218',
                'CC LAB': 'E-201',
                'PROJECT STAGE-1 LAB': 'E-201',
                'IS LAB': 'E-201',
                'FSD LAB': 'E-201',
                'CD LAB': 'E-201',
                'DM LAB': 'E-201',
                'DAA LAB': 'E-201',
                'OS LAB': 'E-201',
                'IOT LAB': 'E-201',
                'DV LAB': 'E-201',
                'CM LAB': 'E-201',
                'JAVA LAB': 'E-201',
                'SE LAB': 'E-201',
                'DBMS LAB': 'E-201',
                'NODE JS LAB': 'E-201'
            };
            return roomMap[key] || '';
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function shouldExcludeFromMainClassTimeTable(subjectName, context) {
            return false;
        }

        function isR22ThreeTwoAIMLContext(context) {
            return Boolean(context) &&
                normalizeClassValue(context.regulation || 'R22') === 'R22' &&
                normalizeAcademicLevelValue(context.year) === '3' &&
                normalizeAcademicLevelValue(context.semester) === '2' &&
                normalizeClassValue(context.branch) === 'AIML' &&
                ['A', 'B'].includes(normalizeClassValue(context.section));
        }

        function enforceR22ThreeTwoAIMLPlans(contexts, selections) {
            const courseSpecs = [
                { key: 'krr', codes: ['AM601PC'], aliases: ['KNOWLEDGE REPRESENTATION AND REASONING', 'KRAR', 'KRR'], name: 'KNOWLEDGE REPRESENTATION AND REASONING', shortLabel: 'KRAR', type: 'theory' },
                { key: 'dataAnalytics', codes: ['AM602PC'], aliases: ['DATA ANALYTICS', 'DA'], name: 'DATA ANALYTICS', shortLabel: 'DA', type: 'theory' },
                { key: 'nlp', codes: ['AM603PC'], aliases: ['NATURAL LANGUAGE PROCESSING', 'NLP'], name: 'NATURAL LANGUAGE PROCESSING', shortLabel: 'NLP', type: 'theory' },
                { key: 'hci', codes: ['AM626PE'], aliases: ['HUMAN COMPUTER INTERACTION', 'HCI'], name: 'HUMAN COMPUTER INTERACTION', shortLabel: 'HCI', type: 'theory' },
                { key: 'res', codes: ['EE611OE'], aliases: ['RENEWABLE ENERGY SOURCES', 'RES'], name: 'RENEWABLE ENERGY SOURCES', shortLabel: 'RES', type: 'theory' },
                { key: 'nlpLab', codes: ['AM604PC'], aliases: ['NATURAL LANGUAGE PROCESSING LAB', 'NATURAL LANGUAGE PROCESSING LABORATORY', 'NLP LAB', 'NLP LABORATORY'], name: 'NATURAL LANGUAGE PROCESSING LABORATORY', shortLabel: 'NLP Lab', type: 'lab' },
                { key: 'dataAnalyticsLab', codes: ['AM605PC'], aliases: ['DATA ANALYTICS LABORATORY', 'DA LAB'], name: 'DATA ANALYTICS LABORATORY', shortLabel: 'DA Lab', type: 'lab' },
                { key: 'aecsLab', codes: ['AE606HS'], aliases: ['ADVANCED ENGLISH COMMUNICATION SKILLS LAB', 'ADVANCED ENGLISH COMMUNICATION SKILLS LABORATORY', 'AECS LAB'], name: 'ADVANCED ENGLISH COMMUNICATION SKILLS LAB', shortLabel: 'AECS Lab', type: 'lab' },
                { key: 'internship', codes: ['AM607PW'], aliases: ['INDUSTRIAL ORIENTED MINI PROJECT/ INTERNSHIP', 'INTERNSHIP'], name: 'INTERNSHIP', shortLabel: 'INTERNSHIP', type: 'lab' }
            ];
            const labDisplayValue = function (assignment) {
                const roomNumber = assignment.labRoomNumber || getStandardLabRoomNumber(assignment.displayName);
                return roomNumber ? assignment.displayName + ' (Room: ' + roomNumber + ')' : assignment.displayName;
            };
            const planBySection = {
                A: {
                    MON: ['aecsLab', '', 'dataAnalytics', 'hci', 'krr', 'nlp'],
                    TUE: ['dataAnalyticsLab', '', 'hci', 'dataAnalytics', 'krr', 'res'],
                    WED: ['nlpLab', '', 'nlp', 'dataAnalytics', 'res', 'SEMINAR'],
                    THU: ['internship', '', 'hci', 'krr', 'nlp', 'res'],
                    FRI: ['dataAnalytics', 'hci', 'krr', 'nlp', 'res', 'SPORTS'],
                    SAT: ['hci', 'dataAnalytics', 'krr', 'nlp', 'res', 'LIBRARY']
                },
                B: {
                    MON: ['dataAnalytics', 'hci', 'krr', 'nlp', 'res', 'LIBRARY'],
                    TUE: ['nlpLab', '', 'dataAnalytics', 'hci', 'krr', 'res'],
                    WED: ['aecsLab', '', 'dataAnalytics', 'nlp', 'res', 'SEMINAR'],
                    THU: ['dataAnalyticsLab', '', 'hci', 'krr', 'nlp', 'res'],
                    FRI: ['internship', '', 'dataAnalytics', 'hci', 'krr', 'nlp'],
                    SAT: ['dataAnalytics', 'hci', 'krr', 'nlp', 'res', 'SPORTS']
                }
            };
            const sectionContexts = {};
            const assignmentsBySection = {};
            const sectionPlans = { A: planBySection.A, B: planBySection.B };
            (contexts || []).forEach(function (context) {
                if (!isR22ThreeTwoAIMLContext(context)) {
                    return;
                }
                const section = normalizeClassValue(context.section);
                const sectionPlan = planBySection[section];
                if (!sectionPlan) {
                    return;
                }
                const classSelections = getSelectionsForClassContext(selections || getStoredSubjectSelections(), context);
                const assignments = {};
                courseSpecs.forEach(function (spec) {
                    const selection = classSelections.find(function (candidate) {
                        const subjectCode = normalizeClassValue(candidate.subjectCode || '').replace(/[^A-Z0-9]/g, '');
                        const subjectName = normalizeSubjectNameForSchedule(candidate.subjectName || '');
                        const matchesCourseCode = spec.codes.some(function (code) {
                            return subjectCode === normalizeClassValue(code).replace(/[^A-Z0-9]/g, '');
                        });
                        const matchesNlpLabName = spec.key === 'nlpLab' &&
                            (subjectName.includes('NATURAL LANGUAGE PROCESSING') || /\bNLP\b/.test(subjectName)) &&
                            /\bLAB(?:ORATORY)?\b/.test(subjectName);
                        return matchesCourseCode || matchesNlpLabName || spec.aliases.some(function (alias) {
                            return subjectName === alias || (alias.length > 8 && subjectName.includes(alias));
                        });
                    }) || null;
                    const subjectName = selection ? selection.subjectName : spec.name;
                    assignments[spec.key] = {
                        selection: selection,
                        subjectName: subjectName,
                        // Use the timetable's canonical course label so every scheduled
                        // period for a selected course is counted under the same name.
                        displayName: spec.shortLabel,
                        facultyKey: selection ? getFacultyScheduleKey(selection) : '',
                        labRoomNumber: spec.key === 'aecsLab'
                            ? 'D-218'
                            : (selection && selection.labRoomNumber ? selection.labRoomNumber : ''),
                        isLab: spec.type === 'lab',
                        isActivity: false,
                        targetHours: spec.type === 'lab' ? 2 : 5,
                        placedHours: 0
                    };
                });
                sectionContexts[section] = context;
                assignmentsBySection[section] = assignments;
            });

            const theoryKeys = courseSpecs.filter(function (spec) {
                return spec.type === 'theory';
            }).map(function (spec) { return spec.key; });
            const pinnedSectionBSlots = new Set(['TUE|2', 'WED|2', 'SAT|0']);
            const getFacultyAt = function (section, day, periodIndex) {
                const sectionPlan = sectionPlans[section];
                const assignments = assignmentsBySection[section] || {};
                const dayPlan = sectionPlan && sectionPlan[day] ? sectionPlan[day] : [];
                for (let startIndex = 0; startIndex <= periodIndex; startIndex += 1) {
                    const assignment = assignments[dayPlan[startIndex]];
                    if (!assignment || !assignment.facultyKey) {
                        continue;
                    }
                    const duration = assignment.isLab ? 2 : 1;
                    if (periodIndex < startIndex + duration) {
                        return assignment.facultyKey;
                    }
                }
                return '';
            };
            const countSectionFacultyClashes = function () {
                let clashes = 0;
                ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'].forEach(function (day) {
                    for (let periodIndex = 0; periodIndex < periodOrder.length; periodIndex += 1) {
                        const facultyA = getFacultyAt('A', day, periodIndex);
                        const facultyB = getFacultyAt('B', day, periodIndex);
                        if (facultyA && facultyA === facultyB) {
                            clashes += 1;
                        }
                    }
                });
                return clashes;
            };
            const findTheorySlots = function (section) {
                const slots = [];
                Object.keys(sectionPlans[section]).forEach(function (day) {
                    sectionPlans[section][day].forEach(function (assignmentKey, periodIndex) {
                        if (theoryKeys.includes(assignmentKey)) {
                            slots.push({ day: day, periodIndex: periodIndex });
                        }
                    });
                });
                return slots;
            };

            if (sectionContexts.A && sectionContexts.B) {
                let clashCount = countSectionFacultyClashes();
                for (let attempt = 0; clashCount > 0 && attempt < 40; attempt += 1) {
                    let bestSwap = null;
                    let bestClashCount = clashCount;
                    ['A', 'B'].forEach(function (section) {
                        const theorySlots = findTheorySlots(section);
                        for (let firstIndex = 0; firstIndex < theorySlots.length; firstIndex += 1) {
                            for (let secondIndex = firstIndex + 1; secondIndex < theorySlots.length; secondIndex += 1) {
                                const first = theorySlots[firstIndex];
                                const second = theorySlots[secondIndex];
                                if (section === 'B' && (pinnedSectionBSlots.has(first.day + '|' + first.periodIndex) || pinnedSectionBSlots.has(second.day + '|' + second.periodIndex))) {
                                    continue;
                                }
                                const dayPlan = sectionPlans[section];
                                const firstKey = dayPlan[first.day][first.periodIndex];
                                const secondKey = dayPlan[second.day][second.periodIndex];
                                if (firstKey === secondKey) {
                                    continue;
                                }
                                dayPlan[first.day][first.periodIndex] = secondKey;
                                dayPlan[second.day][second.periodIndex] = firstKey;
                                const candidateClashes = countSectionFacultyClashes();
                                dayPlan[first.day][first.periodIndex] = firstKey;
                                dayPlan[second.day][second.periodIndex] = secondKey;
                                if (candidateClashes < bestClashCount) {
                                    bestClashCount = candidateClashes;
                                    bestSwap = { section: section, first: first, second: second };
                                }
                            }
                        }
                    });
                    if (!bestSwap) {
                        break;
                    }
                    const plan = sectionPlans[bestSwap.section];
                    const firstKey = plan[bestSwap.first.day][bestSwap.first.periodIndex];
                    plan[bestSwap.first.day][bestSwap.first.periodIndex] = plan[bestSwap.second.day][bestSwap.second.periodIndex];
                    plan[bestSwap.second.day][bestSwap.second.periodIndex] = firstKey;
                    clashCount = bestClashCount;
                }
            }

            let changed = 0;
            ['A', 'B'].forEach(function (section) {
                const context = sectionContexts[section];
                const assignments = assignmentsBySection[section] || {};
                if (!context) {
                    return;
                }
                const displayPlan = {};
                Object.keys(sectionPlans[section]).forEach(function (day) {
                    displayPlan[day] = sectionPlans[section][day].map(function (assignmentKey) {
                        if (!assignmentKey || !assignments[assignmentKey]) {
                            return assignmentKey;
                        }
                        const assignment = assignments[assignmentKey];
                        return assignment.isLab ? labDisplayValue(assignment) : assignment.displayName;
                    });
                });
                applyFixedDisplayPlan(context, displayPlan);
                changed += 1;
            });
            return changed;
        }

        function isR22ThreeTwoITContext(context) {
            return Boolean(context) &&
                normalizeClassValue(context.regulation || 'R22') === 'R22' &&
                normalizeAcademicLevelValue(context.year) === '3' &&
                normalizeAcademicLevelValue(context.semester) === '2' &&
                normalizeBranchValue(context.branch) === 'IT';
        }

        function isR22ThreeTwoAIMLInternship(subjectName) {
            const normalizedName = normalizeSubjectNameForSchedule(subjectName);
            return normalizedName === 'INTERNSHIP' || normalizedName === 'INT' || normalizedName.indexOf('INTERNSHIP') !== -1;
        }

        function isR22ThreeTwoAIMLSeminar(subjectName) {
            return normalizeSubjectNameForSchedule(subjectName) === 'SEMINAR';
        }

        function buildClassAssignments(classSelections, context) {
            const assignmentMap = new Map();
            const normalizedClassSelections = normalizeSubjectSelections(classSelections);
            normalizedClassSelections.forEach(function (selection) {
                const subjectName = (selection.subjectName || '').trim();
                if (shouldExcludeFromMainClassTimeTable(subjectName, context)) {
                    return;
                }
                const displayName = getShortSubjectLabel(subjectName);
                const facultyKey = getFacultyScheduleKey(selection);
                const key = normalizeSubjectNameForSchedule(displayName);
                if (!subjectName || assignmentMap.has(key)) {
                    return;
                }
                const isR25TwoOneReducedLoad = isR25TwoOneITContext(context) || isR25TwoOneAIMLContext(context);
                const isR25TwoTwoIT = isR25TwoTwoITContext(context);
                const isR22ThreeTwoAIML = isR22ThreeTwoAIMLContext(context);
                const isActivity = /^(SPORTS|LIBRARY|MENTORING|EVS\/IKS|VEGS)$/i.test(displayName) ||
                    (isR22ThreeTwoAIML && isR22ThreeTwoAIMLSeminar(displayName));
                const isLab = isLaboratorySubject(subjectName) || isLaboratorySubject(displayName) ||
                    (isR22ThreeTwoAIML && isR22ThreeTwoAIMLInternship(subjectName));
                assignmentMap.set(key, {
                    selection: selection,
                    subjectName: subjectName,
                    displayName: displayName,
                    facultyKey: facultyKey,
                    labRoomNumber: selection.labRoomNumber || '',
                    isLab: isLab,
                    isActivity: isActivity,
                    targetHours: isLab ? 2 : (isR22ThreeTwoAIML && isActivity ? 1 : (isR25TwoTwoIT
                        ? (/^(VEGS|NJRJDU)$/i.test(displayName) ? 2 : (/^(SPORTS|LIBRARY)$/i.test(displayName) ? 1 : 4))
                        : (isR25TwoOneReducedLoad
                        ? (/^(SPORTS|EVS\/IKS|VEGS)$/i.test(displayName) ? 2 : (/^(LIBRARY|MENTORING)$/i.test(displayName) ? 1 : 4))
                        : (isActivity ? 1 : 5)))),
                    placedHours: 0
                });
            });
            return Array.from(assignmentMap.values());
        }

        function canUseClassSlot(context, day, periodIndex, duration, facultyKey, occupancyMap, enforceFacultyGap, assignment, subjectPeriodUsageMap, labRoomOccupancyMap) {
            const slot = getClassSlot(day, periodOrder[periodIndex], context.slots);
            const cell = slot ? slot.closest('td') : null;
            const shouldEnforceFacultyGap = enforceFacultyGap !== false;
            if (!slot || !cell || cell.style.display === 'none' || slot.value.trim()) {
                return false;
            }
            if (hasSubjectPeriodConflict(subjectPeriodUsageMap, assignment, periodIndex, duration)) {
                return false;
            }
            if (hasLabRoomPeriodConflict(labRoomOccupancyMap, assignment, day, periodIndex, duration)) {
                return false;
            }
            if (duration > 1) {
                const nextSlot = getClassSlot(day, periodOrder[periodIndex + 1], context.slots);
                const nextCell = nextSlot ? nextSlot.closest('td') : null;
                if (!nextSlot || !nextCell || nextCell.classList.contains('break-slot') || nextCell.style.display === 'none' || nextSlot.value.trim()) {
                    return false;
                }
            }
            if (hasFacultyConflict(occupancyMap, facultyKey, day, periodIndex, duration)) {
                return false;
            }
            return !shouldEnforceFacultyGap || canFacultyTeachWithGap(occupancyMap, facultyKey, day, periodIndex, duration);
        }

        function placeClassAssignment(context, day, periodIndex, assignment, occupancyMap, enforceFacultyGap, subjectPeriodUsageMap, labRoomOccupancyMap) {
            const assignmentLabelKey = normalizeSubjectNameForSchedule(assignment.displayName || assignment.subjectName);
            const duration = assignment.isLab || (assignmentLabelKey === 'SPORTS' && getSportsDurationForContext(context) === 2) ? 2 : 1;
            const slot = getClassSlot(day, periodOrder[periodIndex], context.slots);
            if (!slot || !canUseClassSlot(context, day, periodIndex, duration, assignment.facultyKey, occupancyMap, enforceFacultyGap, assignment, subjectPeriodUsageMap, labRoomOccupancyMap)) {
                return 0;
            }
            if (duration > 1) {
                if (!mergeSlotWithNextPeriod(slot, getAssignmentSlotDisplayName(assignment), context.slotSelector)) {
                    return 0;
                }
            } else {
                slot.value = getAssignmentSlotDisplayName(assignment);
            }
            reserveFacultyPeriods(occupancyMap, assignment.facultyKey, day, periodIndex, duration);
            reserveSubjectPeriods(subjectPeriodUsageMap, assignment, periodIndex, duration);
            reserveLabRoomPeriods(labRoomOccupancyMap, assignment, day, periodIndex, duration);
            assignment.placedHours += duration;
            return duration;
        }

        function canPlaceLabOnDay(assignment, day, labDaysUsed) {
            if (!assignment.isLab) {
                return true;
            }
            return normalizeClassValue(day) !== 'SAT' && !labDaysUsed.has(day);
        }

        function contextHasAssignmentOnDay(context, assignment, day) {
            if (!assignment || assignment.isActivity) {
                return false;
            }
            const assignmentKey = getAssignmentSubjectKey(assignment);
            return (context && context.slots ? context.slots : []).some(function (slot) {
                return isVisibleFilledClassSlot(slot) &&
                    slot.dataset.day === day &&
                    normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) === assignmentKey;
            });
        }

        function canPlaceWithPreferredSubjectSpacing(context, assignment, day) {
            return !contextHasAssignmentOnDay(context, assignment, day);
        }

        function countClassAssignmentHours(context, assignment) {
            const normalizedDisplayName = normalizeSubjectNameForSchedule(assignment.displayName);
            return (context.slots || []).reduce(function (total, slot) {
                const cell = slot.closest('td');
                if (!cell || cell.style.display === 'none' || normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) !== normalizedDisplayName) {
                    return total;
                }
                return total + (cell.colSpan && cell.colSpan > 1 ? cell.colSpan : 1);
            }, 0);
        }

        function countClassContextHours(context) {
            return (context && context.slots ? context.slots : []).reduce(function (total, slot) {
                const cell = slot.closest('td');
                if (!cell || cell.style.display === 'none' || !slot.value.trim()) {
                    return total;
                }
                return total + (cell.colSpan && cell.colSpan > 1 ? cell.colSpan : 1);
            }, 0);
        }

        function summarizeClassAssignmentsFromSlots(context, assignments) {
            const counts = {};
            let labMergedCount = 0;

            (assignments || []).forEach(function (assignment) {
                const hours = countClassAssignmentHours(context, assignment);
                assignment.placedHours = hours;
                if (hours) {
                    counts[assignment.subjectName] = hours;
                    if (assignment.isLab) {
                        labMergedCount += Math.ceil(hours / 2);
                    }
                }
            });

            return {
                counts: counts,
                labMergedCount: labMergedCount,
                totalHours: countClassContextHours(context)
            };
        }

        function isR22ThreeOneITContext(context) {
            return context &&
                normalizeClassValue(context.regulation || 'R22') === 'R22' &&
                normalizeAcademicLevelValue(context.year) === '3' &&
                normalizeAcademicLevelValue(context.semester) === '1' &&
                normalizeClassValue(context.branch) === 'IT';
        }

        function isR22ThreeOneAIMLContext(context) {
            return context &&
                normalizeClassValue(context.regulation || 'R22') === 'R22' &&
                normalizeAcademicLevelValue(context.year) === '3' &&
                normalizeAcademicLevelValue(context.semester) === '1' &&
                normalizeClassValue(context.branch) === 'AIML';
        }

        function isR22FourOneITContext(context) {
            return context &&
                normalizeClassValue(context.regulation || 'R22') === 'R22' &&
                normalizeAcademicLevelValue(context.year) === '4' &&
                normalizeAcademicLevelValue(context.semester) === '1' &&
                normalizeClassValue(context.branch) === 'IT';
        }

        function isR22FourOneAIMLContext(context) {
            return context &&
                normalizeClassValue(context.regulation || 'R22') === 'R22' &&
                normalizeAcademicLevelValue(context.year) === '4' &&
                normalizeAcademicLevelValue(context.semester) === '1' &&
                normalizeClassValue(context.branch) === 'AIML';
        }

        function isR25TwoOneITContext(context) {
            return context &&
                normalizeClassValue(context.regulation || 'R22') === 'R25' &&
                normalizeAcademicLevelValue(context.year) === '2' &&
                normalizeAcademicLevelValue(context.semester) === '1' &&
                normalizeClassValue(context.branch) === 'IT';
        }

        function isR25TwoTwoITContext(context) {
            return context &&
                normalizeClassValue(context.regulation || 'R22') === 'R25' &&
                normalizeAcademicLevelValue(context.year) === '2' &&
                normalizeAcademicLevelValue(context.semester) === '2' &&
                normalizeClassValue(context.branch) === 'IT';
        }

        function isR22TwoOneITContext(context) {
            return context &&
                normalizeClassValue(context.regulation || 'R22') === 'R22' &&
                normalizeAcademicLevelValue(context.year) === '2' &&
                normalizeAcademicLevelValue(context.semester) === '1' &&
                normalizeClassValue(context.branch) === 'IT';
        }

        function findClassAssignmentByLabel(assignments, label) {
            const wantedLabels = getScheduleLabelsForSubjectName(label).concat([label, getShortSubjectLabel(label)]);
            const wantedKeys = new Set(wantedLabels.map(function (entry) {
                return normalizeSubjectNameForSchedule(entry);
            }));
            const labelIsLab = isLaboratorySubject(label);
            const candidates = (assignments || []).filter(function (assignment) {
                if (labelIsLab !== Boolean(assignment && assignment.isLab)) {
                    return false;
                }
                const assignmentLabels = [assignment.displayName, assignment.subjectName]
                    .concat(getScheduleLabelsForSubjectName(assignment.subjectName || assignment.displayName));
                return assignmentLabels.some(function (entry) {
                    return wantedKeys.has(normalizeSubjectNameForSchedule(entry));
                });
            });
            const exactLabelKey = normalizeSubjectNameForSchedule(getComparableSubjectValue(label));
            return candidates.find(function (assignment) {
                return normalizeSubjectNameForSchedule(assignment.displayName) === exactLabelKey ||
                    normalizeSubjectNameForSchedule(assignment.subjectName) === exactLabelKey;
            }) || candidates[0] || null;
        }

        function createFallbackAssignmentForLabel(label) {
            const normalizedKey = normalizeSubjectNameForSchedule(label);
            const isLab = isLaboratorySubject(label);
            const isActivity = timetableActivityOrder.has(normalizedKey);
            return {
                subjectName: label,
                displayName: label,
                facultyKey: '',
                labRoomNumber: isLab ? getStandardLabRoomNumber(label) : '',
                isLab: isLab,
                isActivity: isActivity,
                targetHours: isLab ? 2 : (isActivity ? 1 : 5),
                placedHours: 0
            };
        }

        function applyR22ThreeOneITFullPlan(context, assignments, occupancyMap, labRoomOccupancyMap) {
            const subjectPeriodUsageMap = createSubjectPeriodUsageMap();
            const counts = {};
            let labMergedCount = 0;
            let totalHours = 0;
            const assignmentByLabel = {};
            const requiredLabels = ['DAA', 'ACD', 'ES', 'DM', 'DDB', 'CD Lab',                 'Data Mining Lab', 'ES Lab', 'Flutter Lab', 'SPORTS', 'LIBRARY', 'MENTORING'];

            requiredLabels.forEach(function (label) {
                assignmentByLabel[label] = findClassAssignmentByLabel(assignments, label) || createFallbackAssignmentForLabel(label);
            });

            const plan = getRequiredFixedPlanForSpec('R22', '3', '1', 'IT', '');
            if (!plan) {
                return null;
            }

            resetClassTimeTableMerges(context.slots);
            context.slots.forEach(function (slot) {
                slot.value = '';
            });

            Object.keys(plan).forEach(function (day) {
                plan[day].forEach(function (label, periodIndex) {
                    if (!label) {
                        return;
                    }
                    const assignment = assignmentByLabel[label];
                    const placedHours = placeClassAssignment(
                        context,
                        day,
                        periodIndex,
                        assignment,
                        occupancyMap,
                        false,
                        subjectPeriodUsageMap,
                        labRoomOccupancyMap
                    );
                    if (placedHours) {
                        counts[assignment.subjectName] = (counts[assignment.subjectName] || 0) + placedHours;
                        totalHours += placedHours;
                        if (assignment.isLab) {
                            labMergedCount += 1;
                        }
                    }
                });
            });

            return {
                counts: counts,
                labMergedCount: labMergedCount,
                totalHours: totalHours
            };
        }

        function applyR25TwoOneITFullPlan(context, assignments, occupancyMap, labRoomOccupancyMap) {
            const subjectPeriodUsageMap = createSubjectPeriodUsageMap();
            const counts = {};
            let labMergedCount = 0;
            let totalHours = 0;
            const assignmentByLabel = {};
            const requiredLabels = ['MSF', 'COA', 'OOPJ', 'OS', 'IoT', 'CM Lab', 'Java Lab', 'OS Lab', 'IoT Lab', 'DV Lab', 'EVS/IKS', 'SPORTS', 'LIBRARY', 'MENTORING'];

            requiredLabels.forEach(function (label) {
                assignmentByLabel[label] = findClassAssignmentByLabel(assignments, label);
            });

            if (requiredLabels.some(function (label) { return !assignmentByLabel[label]; })) {
                return null;
            }

            const plan = getRequiredFixedPlanForSpec('R25', '2', '1', 'IT', '');

            resetClassTimeTableMerges(context.slots);
            context.slots.forEach(function (slot) {
                slot.value = '';
            });

            Object.keys(plan).forEach(function (day) {
                plan[day].forEach(function (label, periodIndex) {
                    if (!label) {
                        return;
                    }
                    const assignment = assignmentByLabel[label];
                    const placedHours = placeClassAssignment(
                        context,
                        day,
                        periodIndex,
                        assignment,
                        occupancyMap,
                        false,
                        subjectPeriodUsageMap,
                        labRoomOccupancyMap
                    );
                    if (placedHours) {
                        counts[assignment.subjectName] = (counts[assignment.subjectName] || 0) + placedHours;
                        totalHours += placedHours;
                        if (assignment.isLab) {
                            labMergedCount += 1;
                        }
                    }
                });
            });

            return {
                counts: counts,
                labMergedCount: labMergedCount,
                totalHours: totalHours
            };
        }

        function applyR25TwoOneAIMLFullPlan(context, assignments, occupancyMap, labRoomOccupancyMap) {
            const subjectPeriodUsageMap = createSubjectPeriodUsageMap();
            const counts = {};
            let labMergedCount = 0;
            let totalHours = 0;
            const assignmentByLabel = {};
            const requiredLabels = ['MSF', 'COA', 'OOPJ', 'SE', 'DBMS', 'CM Lab', 'Java Lab', 'SE Lab', 'DBMS Lab', 'NODE JS Lab', 'VALUE ETHICS AND GENDER SENSITIZATION', 'SPORTS', 'LIBRARY', 'MENTORING'];

            requiredLabels.forEach(function (label) {
                assignmentByLabel[label] = findClassAssignmentByLabel(assignments, label);
            });

            if (requiredLabels.some(function (label) { return !assignmentByLabel[label]; })) {
                return null;
            }

            const plan = getRequiredFixedPlanForSpec('R25', '2', '1', 'AIML', context.section || 'A');

            resetClassTimeTableMerges(context.slots);
            context.slots.forEach(function (slot) {
                slot.value = '';
            });

            Object.keys(plan).forEach(function (day) {
                plan[day].forEach(function (label, periodIndex) {
                    if (!label) {
                        return;
                    }
                    const assignment = assignmentByLabel[label];
                    const placedHours = placeClassAssignment(
                        context,
                        day,
                        periodIndex,
                        assignment,
                        occupancyMap,
                        false,
                        subjectPeriodUsageMap,
                        labRoomOccupancyMap
                    );
                    if (placedHours) {
                        counts[assignment.subjectName] = (counts[assignment.subjectName] || 0) + placedHours;
                        totalHours += placedHours;
                        if (assignment.isLab) {
                            labMergedCount += 1;
                        }
                    }
                });
            });

            return {
                counts: counts,
                labMergedCount: labMergedCount,
                totalHours: totalHours
            };
        }

        function planIsFullySelected(context, assignments, plan) {
            if (!plan) {
                return false;
            }
            const plannedLabels = new Set();
            Object.keys(plan).forEach(function (day) {
                (plan[day] || []).forEach(function (label) {
                    if (label) {
                        plannedLabels.add(normalizeSubjectNameForSchedule(label));
                    }
                });
            });
            if (!plannedLabels.size) {
                return false;
            }
            const selectedLabels = new Set((assignments || []).map(function (assignment) {
                return normalizeSubjectNameForSchedule(assignment.displayName || assignment.subjectName);
            }));
            let covered = true;
            plannedLabels.forEach(function (label) {
                if (!selectedLabels.has(label)) {
                    covered = false;
                }
            });
            return covered;
        }

        // Universal, selection-agnostic enforcement applied to every generated class
        // timetable (main, individual, 2-1/3-1/4-1). Ensures:
        //  - each subject appears at most once per day (one hour per day, no same-day
        //    repeats) by dropping extra same-day occurrences;
        //  - every laboratory subject is a single 2-hour merged block;
        //  - SPORTS is a single 2-hour merged block.
        // Only the subjects already present in the slots are touched; nothing new is added.
        function enforceClassTimeTableSpacingAndMerges(context) {
            if (!context || !context.slots) {
                return;
            }
            const slots = context.slots;
            const days = Array.from(new Set(slots.map(function (slot) {
                return slot.dataset.day || '';
            }).filter(Boolean)));

            // 1. Remove same-day duplicate subject occurrences (keep the first).
            days.forEach(function (day) {
                const seen = new Set();
                slots.forEach(function (slot) {
                    const cell = getTimeTableSlotCell(slot);
                    if (!cell || cell.style.display === 'none' || !slot.value.trim() || slot.dataset.day !== day) {
                        return;
                    }
                    const value = getComparableSubjectValue(slot.value);
                    const key = normalizeSubjectNameForSchedule(value);
                    if (isLaboratoryScheduleValue(value) || normalizeSubjectNameForSchedule(value) === 'SPORTS') {
                        return;
                    }
                    if (seen.has(key)) {
                        slot.value = '';
                        if (cell.colSpan && cell.colSpan > 1) {
                            restoreClassLabMergesFromValues(slots);
                        }
                        return;
                    }
                    seen.add(key);
                });
            });

            // 2. Ensure each lab is a single 2-hour merged block.
            slots.forEach(function (slot) {
                const cell = getTimeTableSlotCell(slot);
                if (!cell || cell.style.display === 'none' || !slot.value.trim()) {
                    return;
                }
                const value = getComparableSubjectValue(slot.value);
                if (!isLaboratoryScheduleValue(value)) {
                    return;
                }
                if (!(cell.colSpan && cell.colSpan > 1)) {
                    mergeSlotWithNextPeriod(slot, getAssignmentSlotDisplayName({
                        displayName: value,
                        subjectName: value,
                        isLab: true,
                        labRoomNumber: extractLabRoomNumber(slot.value)
                    }), context.slotSelector);
                }
            });

            repairDuplicateLabDays(context);

            // 3. Ensure SPORTS matches the context: a single 2-hour merged block for 2-1,
            //    or a single 1-hour block for 3-1 (and other levels).
            const sportsTargetHours = getSportsDurationForContext(context);
            days.forEach(function (day) {
                let sportsCount = 0;
                slots.forEach(function (slot) {
                    const cell = getTimeTableSlotCell(slot);
                    if (!cell || cell.style.display === 'none' || !slot.value.trim() || slot.dataset.day !== day) {
                        return;
                    }
                    const value = getComparableSubjectValue(slot.value);
                    if (normalizeSubjectNameForSchedule(value) === 'SPORTS') {
                        sportsCount += (cell.colSpan && cell.colSpan > 1) ? 2 : 1;
                    }
                });
                if (sportsCount > sportsTargetHours) {
                    let removed = 0;
                    const target = sportsCount - sportsTargetHours;
                    slots.forEach(function (slot) {
                        if (removed >= target) {
                            return;
                        }
                        const cell = getTimeTableSlotCell(slot);
                        if (!cell || cell.style.display === 'none' || !slot.value.trim() || slot.dataset.day !== day) {
                            return;
                        }
                        const value = getComparableSubjectValue(slot.value);
                        if (normalizeSubjectNameForSchedule(value) === 'SPORTS') {
                            slot.value = '';
                            if (cell.colSpan && cell.colSpan > 1) {
                                restoreClassLabMergesFromValues(slots);
                            }
                            removed += 1;
                        }
                    });
                }
                if (sportsTargetHours >= 2 && sportsCount === 1) {
                    for (let periodIndex = 0; periodIndex < periodOrder.length; periodIndex += 1) {
                        const slot = getClassSlot(day, periodOrder[periodIndex], slots);
                        const cell = slot ? getTimeTableSlotCell(slot) : null;
                        if (!slot || !cell || cell.style.display === 'none' || slot.value.trim()) {
                            continue;
                        }
                        const nextSlot = getClassSlot(day, periodOrder[periodIndex + 1], slots);
                        const nextCell = nextSlot ? getTimeTableSlotCell(nextSlot) : null;
                        if (nextSlot && nextCell && nextCell.style.display !== 'none' && !nextSlot.value.trim()) {
                            mergeSlotWithNextPeriod(slot, 'SPORTS', context.slotSelector);
                            break;
                        }
                    }
                }
            });
        }
        function applyTwoOnePlanForSelectedSubjects(context, assignments, plan) {
            if (!plan) {
                return false;
            }
            const selectedKeys = new Set((assignments || []).map(function (assignment) {
                return normalizeSubjectNameForSchedule(assignment.displayName || assignment.subjectName);
            }));
            const filteredPlan = {};
            let hasSelected = false;
            Object.keys(plan).forEach(function (day) {
                const kept = (plan[day] || []).filter(function (label) {
                    if (!label) {
                        return false;
                    }
                    const isSelected = selectedKeys.has(normalizeSubjectNameForSchedule(label));
                    if (isSelected) {
                        hasSelected = true;
                    }
                    return isSelected;
                });
                filteredPlan[day] = kept;
            });
            if (!hasSelected) {
                return false;
            }
            return applyFixedDisplayPlan(context, filteredPlan);
        }

        // Constraint-driven generator for 2-1 and 3-1 timetables. Guarantees, for the
        // user's selected subjects only (nothing is injected):
        //  - 2-1: every theory subject = exactly 4 hours/week; 3-1: exactly 5 hours/week.
        //  - each subject appears at most once per day (no same-day repeat);
        //  - each subject's occurrences use distinct period positions (no "same hour" on
        //    different days, e.g. not 1st hour every day);
        //  - labs are single 2-hour merged blocks; SPORTS is a 2-hour merged block for 2-1
        //    and a single 1-hour block for 3-1;
        //  - faculty is never double-booked (uses the shared occupancy maps).
        function generateBalancedClassTimeTable(context, assignments, occupancyMap, labRoomOccupancyMap) {
            const year = normalizeAcademicLevelValue(context.year);
            if (year !== '2' && year !== '3') {
                return null;
            }
            const isTwoOne = year === '2';
            const isSports = function (assignment) {
                return normalizeSubjectNameForSchedule(assignment.displayName || assignment.subjectName) === normalizeSubjectNameForSchedule('SPORTS');
            };
            const subjectKeyOf = function (assignment) {
                return normalizeSubjectNameForSchedule(assignment.displayName || assignment.subjectName);
            };
            const days = Array.from(new Set((context.slots || []).map(function (slot) {
                return slot.dataset.day || '';
            }).filter(Boolean)));

            const usedPeriods = new Map();
            const usedDays = new Map();
            const labDaysUsed = new Set();
            const counts = {};
            let labMergedCount = 0;
            let totalHours = 0;

            function subjectUsedPeriods(key) {
                if (!usedPeriods.has(key)) {
                    usedPeriods.set(key, new Set());
                }
                return usedPeriods.get(key);
            }
            function subjectUsedDays(key) {
                if (!usedDays.has(key)) {
                    usedDays.set(key, new Set());
                }
                return usedDays.get(key);
            }
            function slotFree(day, periodIndex) {
                const slot = getClassSlot(day, periodOrder[periodIndex], context.slots);
                const cell = slot ? getTimeTableSlotCell(slot) : null;
                return Boolean(slot) && cell && cell.style.display !== 'none' && !slot.value.trim();
            }
            function facultyClashes(day, periodIndex, duration, facultyKey) {
                return Boolean(occupancyMap) && Boolean(facultyKey) &&
                    hasFacultyConflict(occupancyMap, facultyKey, day, periodIndex, duration);
            }
            function violatesDistinctHour(day, periodIndex, duration, key) {
                for (let k = 0; k < duration; k += 1) {
                    if (subjectUsedPeriods(key).has(periodIndex + k)) {
                        return true;
                    }
                }
                return false;
            }
            function placeSingle(assignment, day, periodIndex) {
                const key = subjectKeyOf(assignment);
                const slot = getClassSlot(day, periodOrder[periodIndex], context.slots);
                slot.value = getAssignmentSlotDisplayName(assignment);
                subjectUsedPeriods(key).add(periodIndex);
                subjectUsedDays(key).add(day);
                if (occupancyMap && assignment.facultyKey) {
                    reserveFacultyPeriods(occupancyMap, assignment.facultyKey, day, periodIndex, 1);
                }
                counts[assignment.subjectName] = (counts[assignment.subjectName] || 0) + 1;
                totalHours += 1;
            }
            function placeMerged(assignment, day, startPeriodIndex, duration) {
                const key = subjectKeyOf(assignment);
                const slot = getClassSlot(day, periodOrder[startPeriodIndex], context.slots);
                mergeSlotWithNextPeriod(slot, getAssignmentSlotDisplayName(assignment), context.slotSelector);
                for (let k = 0; k < duration; k += 1) {
                    subjectUsedPeriods(key).add(startPeriodIndex + k);
                }
                subjectUsedDays(key).add(day);
                if (occupancyMap && assignment.facultyKey) {
                    reserveFacultyPeriods(occupancyMap, assignment.facultyKey, day, startPeriodIndex, duration);
                }
                if (labRoomOccupancyMap) {
                    reserveLabRoomPeriods(labRoomOccupancyMap, assignment, day, startPeriodIndex, duration);
                }
                counts[assignment.subjectName] = (counts[assignment.subjectName] || 0) + duration;
                totalHours += duration;
                labMergedCount += 1;
            }
            function targetOf(assignment) {
                if (isR25TwoTwoITContext(context)) {
                    return assignment.targetHours || 1;
                }
                if (assignment.isLab) {
                    return 2;
                }
                if (isSports(assignment)) {
                    return isTwoOne ? 2 : 1;
                }
                if (assignment.isActivity) {
                    return assignment.targetHours || 1;
                }
                return isTwoOne ? 4 : 5;
            }
            function placeSingleHours(assignment, target, idx) {
                const key = subjectKeyOf(assignment);
                let placed = 0;
                let attempts = 0;
                let periodCursor = idx % periodOrder.length;
                while (placed < target && attempts < 300) {
                    attempts += 1;
                    let placedThisSubject = false;
                    for (let d = 0; d < days.length && !placedThisSubject; d += 1) {
                        const day = days[(idx + placed + d) % days.length];
                        if (subjectUsedDays(key).has(day)) {
                            continue;
                        }
                        for (let p = 0; p < periodOrder.length && !placedThisSubject; p += 1) {
                            const periodIndex = (periodCursor + p) % periodOrder.length;
                            if (subjectUsedPeriods(key).has(periodIndex)) {
                                continue;
                            }
                            if (!slotFree(day, periodIndex)) {
                                continue;
                            }
                            if (facultyClashes(day, periodIndex, 1, assignment.facultyKey)) {
                                continue;
                            }
                            placeSingle(assignment, day, periodIndex);
                            placed += 1;
                            placedThisSubject = true;
                            periodCursor = (periodCursor + 1) % periodOrder.length;
                        }
                    }
                    if (!placedThisSubject) {
                        break;
                    }
                }
            }
            function placeMergedBlock(assignment, idx, duration) {
                const key = subjectKeyOf(assignment);
                const startCandidates = requiresMorningTheoryCoverage(context) ? [3, 0] : [0, 3];
                let placed = false;
                for (let d = 0; d < days.length && !placed; d += 1) {
                    const day = days[(idx + d) % days.length];
                    if (subjectUsedDays(key).has(day) || (assignment.isLab && labDaysUsed.has(day)) || normalizeClassValue(day) === 'SAT') {
                        continue;
                    }
                    for (let s = 0; s < startCandidates.length && !placed; s += 1) {
                        const start = startCandidates[s];
                        const end = start + 1;
                        if (!slotFree(day, start) || !slotFree(day, end)) {
                            continue;
                        }
                        if (violatesDistinctHour(day, start, duration, key)) {
                            continue;
                        }
                        if (facultyClashes(day, start, duration, assignment.facultyKey)) {
                            continue;
                        }
                        if (hasLabRoomPeriodConflict(labRoomOccupancyMap, assignment, day, start, duration)) {
                            continue;
                        }
                        placeMerged(assignment, day, start, duration);
                        if (assignment.isLab) {
                            labDaysUsed.add(day);
                        }
                        placed = true;
                    }
                }
            }

            const labs = (assignments || []).filter(function (a) { return a.isLab; });
            const sports = (assignments || []).filter(function (a) { return isSports(a); });
            const otherActivities = (assignments || []).filter(function (a) {
                return !a.isLab && !isSports(a) && a.isActivity;
            });
            const theory = (assignments || []).filter(function (a) {
                return !a.isLab && !isSports(a) && !a.isActivity;
            });

            if (requiresMorningTheoryCoverage(context)) {
                theory.forEach(function (assignment, assignmentIndex) {
                    const key = subjectKeyOf(assignment);
                    if (targetOf(assignment) < 1) {
                        return;
                    }
                    for (let dayOffset = 0; dayOffset < days.length; dayOffset += 1) {
                        const day = days[(assignmentIndex + dayOffset) % days.length];
                        if (subjectUsedDays(key).has(day) || subjectUsedPeriods(key).has(0) || !slotFree(day, 0)) {
                            continue;
                        }
                        if (facultyClashes(day, 0, 1, assignment.facultyKey)) {
                            continue;
                        }
                        placeSingle(assignment, day, 0);
                        break;
                    }
                });
            }

            labs.forEach(function (assignment, idx) {
                placeMergedBlock(assignment, idx, 2);
            });
            sports.forEach(function (assignment, idx) {
                const target = targetOf(assignment);
                if (target >= 2) {
                    placeMergedBlock(assignment, idx, 2);
                } else {
                    placeSingleHours(assignment, 1, idx);
                }
            });
            otherActivities.forEach(function (assignment, idx) {
                placeSingleHours(assignment, targetOf(assignment), idx);
            });
            theory.forEach(function (assignment, idx) {
                placeSingleHours(assignment, targetOf(assignment), idx);
            });

            return { counts: counts, labMergedCount: labMergedCount, totalHours: totalHours };
        }

        function generateClassTimeTableSlotsForContext(context, classSelections, occupancyMap, labRoomOccupancyMap) {
            const assignments = buildClassAssignments(classSelections, context);
            const shouldUseFlexibleLabPlacement = hasLabRoomSelections(classSelections);
            const placementAssignments = assignments.slice().sort(function (left, right) {
                if (left.isLab !== right.isLab) {
                    return left.isLab ? -1 : 1;
                }
                if (left.isActivity !== right.isActivity) {
                    return left.isActivity ? 1 : -1;
                }
                return 0;
            });
            const counts = {};
            const labDaysUsed = new Set();
            const subjectPeriodUsageMap = createSubjectPeriodUsageMap();
            let labMergedCount = 0;
            let totalHours = 0;

            resetClassTimeTableMerges(context.slots);
            context.slots.forEach(function (slot) {
                slot.value = '';
            });

            if (!assignments.length) {
                return { counts: counts, labMergedCount: 0, totalHours: 0 };
            }

            // For 2-2 (II-II) and 3-2 (III-II) timetables, use the balanced generator. It
            // spreads every selected subject across distinct periods (hours 1-6) and
            // distinct days (Monday-Saturday) so no subject is piled into the same hour,
            // keeps labs as 2-hour merged blocks, and sets SPORTS to a 2-hour merged block
            // for 2-1 or a single 1-hour block for 3-1. Works for any user-selected subjects.
            const contextYear = normalizeAcademicLevelValue(context.year);
            if (contextYear === '2' || contextYear === '3') {
                const balanced = generateBalancedClassTimeTable(context, assignments, occupancyMap, labRoomOccupancyMap);
                if (balanced && balanced.totalHours > 0) {
                    return balanced;
                }
            }

            // For 4-1 timetables (and as a fallback), place the user's selected subjects using
            // the fixed layout for that class, filtered to only those selections. The
            // layout guarantees each subject appears at most once per day (one hour per
            // day, no same-day repeats) and that labs and SPORTS are merged into 2-hour
            // blocks. Subjects not chosen by the user are never injected.
            if (isR25TwoOneITContext(context) || isR22TwoOneITContext(context) ||
                isR25TwoOneAIMLContext(context) || isR22ThreeOneITContext(context) ||
                isR22ThreeOneAIMLContext(context) || isR22FourOneITContext(context) ||
                isR22FourOneAIMLContext(context)) {
                const fixedPlan = getRequiredFixedPlanForSpec(
                    context.regulation,
                    context.year,
                    context.semester,
                    context.branch,
                    context.section
                );
                if (applyTwoOnePlanForSelectedSubjects(context, assignments, fixedPlan)) {
                    return summarizeClassAssignmentsFromSlots(context, assignments);
                }
            }

            if (isR25TwoOneITContext(context) && hasCompleteR25TwoOneITLoad(context)) {
                return summarizeClassAssignmentsFromSlots(context, assignments);
            }

            if (isR25TwoOneAIMLContext(context) && hasCompleteR25TwoOneAIMLLoad(context)) {
                return summarizeClassAssignmentsFromSlots(context, assignments);
            }

            if (isR22ThreeOneAIMLContext(context) && hasCompleteR22ThreeOneAIMLLoad(context)) {
                return summarizeClassAssignmentsFromSlots(context, assignments);
            }

            if (isR22FourOneITContext(context) && hasCompleteR22FourOneITLoad(context)) {
                return summarizeClassAssignmentsFromSlots(context, assignments);
            }

            if (isR22FourOneAIMLContext(context) && hasCompleteR22FourOneAIMLLoad(context)) {
                return summarizeClassAssignmentsFromSlots(context, assignments);
            }

            const days = Array.from(new Set(context.slots.map(function (slot) {
                return slot.dataset.day || '';
            }).filter(Boolean)));

            if (requiresMorningTheoryCoverage(context)) {
                const theoryAssignments = assignments.filter(function (assignment) {
                    return !assignment.isLab && !assignment.isActivity &&
                        normalizeSubjectNameForSchedule(assignment.displayName || assignment.subjectName) !== 'SPORTS';
                });
                theoryAssignments.forEach(function (assignment, assignmentIndex) {
                    if ((assignment.targetHours || 0) < 1) {
                        return;
                    }
                    for (let dayOffset = 0; dayOffset < days.length; dayOffset += 1) {
                        const day = days[(assignmentIndex + dayOffset) % days.length];
                        if (contextHasAssignmentOnDay(context, assignment, day)) {
                            continue;
                        }
                        if (!canUseClassSlot(context, day, 0, 1, assignment.facultyKey, occupancyMap, true, assignment, subjectPeriodUsageMap, labRoomOccupancyMap)) {
                            continue;
                        }
                        const placedHours = placeClassAssignment(context, day, 0, assignment, occupancyMap, true, subjectPeriodUsageMap, labRoomOccupancyMap);
                        if (placedHours) {
                            counts[assignment.subjectName] = (counts[assignment.subjectName] || 0) + placedHours;
                            totalHours += placedHours;
                            break;
                        }
                    }
                });
            }

            days.forEach(function (day, dayIndex) {
                const dailySubjects = new Set((context.slots || []).filter(function (slot) {
                    return slot.dataset.day === day && isVisibleFilledClassSlot(slot);
                }).map(function (slot) {
                    const assignment = findClassAssignmentByLabel(assignments, getComparableSubjectValue(slot.value));
                    return assignment && !assignment.isActivity ? assignment.subjectName : '';
                }).filter(Boolean));
                periodOrder.forEach(function (period, periodIndex) {
                    for (let offset = 0; offset < placementAssignments.length; offset += 1) {
                        const assignment = placementAssignments[(dayIndex + periodIndex + offset) % placementAssignments.length];
                        const remainingHours = assignment.targetHours - assignment.placedHours;
                        const duration = assignment.isLab ? 2 : ((assignment.subjectName || '').toUpperCase() === 'SPORTS' && getSportsDurationForContext(context) === 2 ? 2 : 1);
                        if (remainingHours < duration || (!assignment.isActivity && dailySubjects.has(assignment.subjectName))) {
                            continue;
                        }
                        if (assignment.isLab && ![0, 3].includes(periodIndex)) {
                            continue;
                        }
                        if (!canPlaceLabOnDay(assignment, day, labDaysUsed)) {
                            continue;
                        }
                        if (!canUseClassSlot(context, day, periodIndex, duration, assignment.facultyKey, occupancyMap, true, assignment, subjectPeriodUsageMap, labRoomOccupancyMap)) {
                            continue;
                        }
                        const placedHours = placeClassAssignment(context, day, periodIndex, assignment, occupancyMap, true, subjectPeriodUsageMap, labRoomOccupancyMap);
                        if (placedHours) {
                            counts[assignment.subjectName] = (counts[assignment.subjectName] || 0) + placedHours;
                            totalHours += placedHours;
                            if (!assignment.isActivity) {
                                dailySubjects.add(assignment.subjectName);
                            }
                            if (assignment.isLab) {
                                labDaysUsed.add(day);
                            }
                            if (duration > 1) {
                                labMergedCount += 1;
                            }
                            break;
                        }
                    }
                });
            });

            placementAssignments.forEach(function (assignment, assignmentIndex) {
                let guard = 0;
                while (assignment.placedHours < assignment.targetHours && guard < 100) {
                    guard += 1;
                    let placed = false;
                    for (let dayOffset = 0; dayOffset < days.length && !placed; dayOffset += 1) {
                        const day = days[(assignmentIndex + dayOffset) % days.length];
                        for (let periodIndex = 0; periodIndex < periodOrder.length; periodIndex += 1) {
                            const duration = assignment.isLab ? 2 : ((assignment.subjectName || '').toUpperCase() === 'SPORTS' && getSportsDurationForContext(context) === 2 ? 2 : 1);
                            if (assignment.isLab && ![0, 3].includes(periodIndex)) {
                                continue;
                            }
                            if (!canPlaceWithPreferredSubjectSpacing(context, assignment, day)) {
                                continue;
                            }
                            if (!canPlaceLabOnDay(assignment, day, labDaysUsed)) {
                                continue;
                            }
                            if (!canUseClassSlot(context, day, periodIndex, duration, assignment.facultyKey, occupancyMap, true, assignment, subjectPeriodUsageMap, labRoomOccupancyMap)) {
                                continue;
                            }
                            const placedHours = placeClassAssignment(context, day, periodIndex, assignment, occupancyMap, true, subjectPeriodUsageMap, labRoomOccupancyMap);
                            if (placedHours) {
                                counts[assignment.subjectName] = (counts[assignment.subjectName] || 0) + placedHours;
                                totalHours += placedHours;
                                if (assignment.isLab) {
                                    labDaysUsed.add(day);
                                }
                                if (duration > 1) {
                                    labMergedCount += 1;
                                }
                                placed = true;
                                break;
                            }
                        }
                    }
                    if (!placed) {
                        break;
                    }
                }
            });

            placementAssignments.forEach(function (assignment, assignmentIndex) {
                let guard = 0;
                while (assignment.placedHours < assignment.targetHours && guard < 100) {
                    guard += 1;
                    let placed = false;
                    for (let dayOffset = 0; dayOffset < days.length && !placed; dayOffset += 1) {
                        const day = days[(assignmentIndex + dayOffset) % days.length];
                        for (let periodIndex = 0; periodIndex < periodOrder.length; periodIndex += 1) {
                            const duration = assignment.isLab ? 2 : ((assignment.subjectName || '').toUpperCase() === 'SPORTS' && getSportsDurationForContext(context) === 2 ? 2 : 1);
                            if (assignment.isLab && ![0, 3].includes(periodIndex)) {
                                continue;
                            }
                            if (!canPlaceWithPreferredSubjectSpacing(context, assignment, day)) {
                                continue;
                            }
                            if (!canPlaceLabOnDay(assignment, day, labDaysUsed)) {
                                continue;
                            }
                            if (!canUseClassSlot(context, day, periodIndex, duration, assignment.facultyKey, occupancyMap, false, assignment, subjectPeriodUsageMap, labRoomOccupancyMap)) {
                                continue;
                            }
                            const placedHours = placeClassAssignment(context, day, periodIndex, assignment, occupancyMap, false, subjectPeriodUsageMap, labRoomOccupancyMap);
                            if (placedHours) {
                                counts[assignment.subjectName] = (counts[assignment.subjectName] || 0) + placedHours;
                                totalHours += placedHours;
                                if (assignment.isLab) {
                                    labDaysUsed.add(day);
                                }
                                if (duration > 1) {
                                    labMergedCount += 1;
                                }
                                placed = true;
                                break;
                            }
                        }
                    }
                    if (!placed) {
                        break;
                    }
                }
            });

            placementAssignments.forEach(function (assignment, assignmentIndex) {
                assignment.placedHours = Math.max(assignment.placedHours, countClassAssignmentHours(context, assignment));
                let guard = 0;
                while (assignment.placedHours < assignment.targetHours && guard < 100) {
                    guard += 1;
                    let placed = false;
                    for (let dayOffset = 0; dayOffset < days.length && !placed; dayOffset += 1) {
                        const day = days[(assignmentIndex + dayOffset) % days.length];
                        for (let periodIndex = 0; periodIndex < periodOrder.length; periodIndex += 1) {
                            const duration = assignment.isLab ? 2 : ((assignment.subjectName || '').toUpperCase() === 'SPORTS' && getSportsDurationForContext(context) === 2 ? 2 : 1);
                            if (assignment.isLab && ![0, 3].includes(periodIndex)) {
                                continue;
                            }
                            if (!canPlaceWithPreferredSubjectSpacing(context, assignment, day)) {
                                continue;
                            }
                            if (!canPlaceLabOnDay(assignment, day, labDaysUsed)) {
                                continue;
                            }
                            if (!canUseClassSlot(context, day, periodIndex, duration, assignment.facultyKey, occupancyMap, false, assignment, subjectPeriodUsageMap, labRoomOccupancyMap)) {
                                continue;
                            }
                            const placedHours = placeClassAssignment(context, day, periodIndex, assignment, occupancyMap, false, subjectPeriodUsageMap, labRoomOccupancyMap);
                            if (placedHours) {
                                counts[assignment.subjectName] = (counts[assignment.subjectName] || 0) + placedHours;
                                totalHours += placedHours;
                                if (assignment.isLab) {
                                    labDaysUsed.add(day);
                                }
                                if (duration > 1) {
                                    labMergedCount += 1;
                                }
                                placed = true;
                                break;
                            }
                        }
                    }
                    if (!placed) {
                        break;
                    }
                }
            });

            placementAssignments.forEach(function (assignment, assignmentIndex) {
                assignment.placedHours = Math.max(assignment.placedHours, countClassAssignmentHours(context, assignment));
                let guard = 0;
                while (assignment.placedHours < assignment.targetHours && guard < 100) {
                    guard += 1;
                    let placed = false;
                    for (let dayOffset = 0; dayOffset < days.length && !placed; dayOffset += 1) {
                        const day = days[(assignmentIndex + dayOffset) % days.length];
                        for (let periodIndex = 0; periodIndex < periodOrder.length; periodIndex += 1) {
                            const duration = assignment.isLab ? 2 : ((assignment.subjectName || '').toUpperCase() === 'SPORTS' && getSportsDurationForContext(context) === 2 ? 2 : 1);
                            if (assignment.isLab && ![0, 3].includes(periodIndex)) {
                                continue;
                            }
                            if (!canPlaceLabOnDay(assignment, day, labDaysUsed)) {
                                continue;
                            }
                            if (!canUseClassSlot(context, day, periodIndex, duration, assignment.facultyKey, occupancyMap, false, assignment, null, labRoomOccupancyMap)) {
                                continue;
                            }
                            const placedHours = placeClassAssignment(context, day, periodIndex, assignment, occupancyMap, false, null, labRoomOccupancyMap);
                            if (placedHours) {
                                counts[assignment.subjectName] = (counts[assignment.subjectName] || 0) + placedHours;
                                totalHours += placedHours;
                                if (assignment.isLab) {
                                    labDaysUsed.add(day);
                                }
                                if (duration > 1) {
                                    labMergedCount += 1;
                                }
                                placed = true;
                                break;
                            }
                        }
                    }
                    if (!placed) {
                        break;
                    }
                }
            });

            enforceClassTimeTableSpacingAndMerges(context);
            return summarizeClassAssignmentsFromSlots(context, assignments);
        }

        function getScheduleLabelsForSelection(selection) {
            const labels = getScheduleLabelsForSubjectName(selection.subjectName || '');
            const code = normalizeClassValue(selection.subjectCode || '');
            const facultyName = normalizeSubjectNameForSchedule(selection.facultyName || '');
            const compactFacultyName = facultyName.replace(/[^A-Z0-9]/g, '');
            const labelsByCode = {
                AM604PC: ['NLP Lab'],
                CS501PC: ['DAA'],
                IT502PC: ['ACD'],
                IT503PC: ['ES'],
                '2505304': ['COA'],
                '2599303': ['MSF'],
                '2599304': ['EVS/IKS'],
                '2599305': ['VEGS'],
                CM304PC: ['COA'],
                CS304PC: ['COA'],
                '2505305': ['OOPJ'],
                '2505306': ['SE'],
                '2505307': ['DBMS'],
                '2505309': ['SE Lab'],
                '2505310': ['DBMS Lab'],
                '2505311': ['NODE JS Lab'],
                '2512301': ['OS'],
                '2504310': ['IoT'],
                '2512303': ['DV Lab'],
                CS524PE: ['DDB'],
                IT512PE: ['DM'],
                IT705PC: ['Project Stage-1 Lab'],
                AM705PC: ['Project Stage-1 Lab'],
                IT504PC: ['CD Lab'],
                IT505PC: ['ES Lab'],
                IT532PE: ['Data Mining Lab'],
                IT503PC: ['ES', 'ES Lab'],
                '2512302': ['OS Lab'],
                '2505405': ['OS Lab'],
                '2504311': ['IoT Lab'],
                '2505308': ['Java Lab'],
                '2599302': ['CM Lab'],
                CS507PC: ['Flutter Lab']
            };

            (labelsByCode[code] || []).forEach(function (label) {
                if (!labels.includes(label)) {
                    labels.push(label);
                }
            });

            if (compactFacultyName.includes('KRAMAKRISHNA')) {
                ['ES Lab', 'EMBEDDED SYSTEMS LABORATORY'].forEach(function (label) {
                    if (!labels.includes(label)) {
                        labels.push(label);
                    }
                });
            }

            return labels;
        }

        function getScheduleLabelsForSubjectName(subjectName) {
            const normalized = normalizeSubjectNameForSchedule(subjectName);
            const labels = [subjectName];

            if ((normalized.includes('NATURAL LANGUAGE PROCESSING') || /\bNLP\b/.test(normalized)) &&
                /\bLAB(?:ORATORY)?\b/.test(normalized)) {
                labels.push('NLP Lab');
            }

            if (normalized.includes('DESIGN AND ANALYSIS OF ALGORITHMS')) {
                labels.push('DAA');
            }
            if (normalized.includes('DATA COMMUNICATIONS AND COMPUTER NETWORKS') ||
                normalized.includes('DATA COMMUNICATION AND COMPUTER NETWORKS')) {
                labels.push('DCACN');
            }
            if (normalized.includes('AUTOMATA AND COMPILER DESIGN')) {
                labels.push('ACD');
            }
            if (normalized.includes('COMPUTER ORGANIZATION AND ARCHITECTURE') ||
                normalized.includes('COMPUTER ORGANIZATION AND MICROPROCESSOR')) {
                labels.push('COA');
            }
            if (normalized.includes('MATHEMATICAL AND STATISTICAL FOUNDATIONS')) {
                labels.push('MSF');
            }
            if (normalized.includes('ENVIRONMENTAL SCIENCE') && normalized.includes('INDIAN KNOWLEDGE SYSTEM')) {
                labels.push('EVS/IKS');
            }
            if (normalized.includes('VALUE ETHICS') && normalized.includes('GENDER SENSITIZATION')) {
                labels.push('VEGS');
            }
            if (normalized.includes('SOFTWARE ENGINEERING LABORATORY') || normalized.includes('SOFTWARE ENGINEERING LAB')) {
                labels.push('SE Lab');
            } else if (normalized.includes('SOFTWARE ENGINEERING')) {
                labels.push('SE');
                labels.push('SE Lab');
            }
            if (normalized.includes('DATABASE MANAGEMENT SYSTEMS LABORATORY') || normalized.includes('DATABASE MANAGEMENT SYSTEMS LAB')) {
                labels.push('DBMS Lab');
            } else if (normalized.includes('DATABASE MANAGEMENT SYSTEMS')) {
                labels.push('DBMS');
                labels.push('DBMS Lab');
            }
            if (normalized.includes('EMBEDDED SYSTEMS LABORATORY') || normalized.includes('EMBEDDED SYSTEMS LAB')) {
                labels.push('ES Lab');
            } else if (normalized.includes('EMBEDDED SYSTEM') || normalized.includes('EMBEDDED SYSTEMS')) {
                labels.push('ES');
                labels.push('ES Lab');
            }
            if (normalized.includes('DATA MINING LABORATORY') || normalized.includes('DATA MINING LAB')) {
                labels.push('Data Mining Lab');
            } else if (normalized.includes('DATA MINING')) {
                labels.push('DM');
            }
            if (normalized.includes('DATA VISUALIZATION')) {
                labels.push('DV Lab');
                labels.push('DV');
            }
            if (normalized.includes('DISTRIBUTED DATABASES')) {
                labels.push('DDB');
            }
            if (normalized.includes('COMPILER DESIGN LABORATORY') || normalized.includes('COMPILER DESIGN LAB')) {
                labels.push('CD Lab');
            }
            if (normalized.includes('OPERATING SYSTEMS LABORATORY') || normalized.includes('OPERATING SYSTEMS LAB')) {
                labels.push('OS Lab');
            } else if (normalized.includes('OPERATING SYSTEMS')) {
                labels.push('OS');
                labels.push('OS Lab');
            }
            if (normalized.includes('INTERNET OF THINGS LABORATORY') || normalized.includes('INTERNET OF THINGS LAB') || normalized.includes('IOT LAB')) {
                labels.push('IoT Lab');
            } else if (normalized.includes('INTRODUCTION TO IOT') || normalized.includes('INTERNET OF THINGS') || normalized.includes('IOT')) {
                labels.push('IoT');
                labels.push('IoT Lab');
            }
            if (normalized.includes('OBJECT ORIENTED PROGRAMMING THROUGH JAVA LABORATORY') || normalized.includes('JAVA LABORATORY') || normalized.includes('JAVA LAB')) {
                labels.push('Java Lab');
            } else if (normalized.includes('OBJECT ORIENTED PROGRAMMING THROUGH JAVA')) {
                labels.push('OOPJ');
                labels.push('Java Lab');
            }
            if (normalized.includes('COMPUTATIONAL MATHEMATICS LABORATORY') || normalized.includes('COMPUTATIONAL MATHEMATICS LAB')) {
                labels.push('CM Lab');
            }
            if (normalized.includes('POWER BI') || normalized.includes('POWERBI') || normalized.includes('TABLEAU') || normalized.includes('GOOGLE CHART')) {
                labels.push('DV Lab');
                labels.push('DV');
            }
            if (normalized.includes('SKILL DEVELOPMENT COURSE') &&
                (normalized.includes('NODE JS') || normalized.includes('REACT JS') || normalized.includes('DJANGO'))) {
                labels.push('NODE JS Lab');
            }
            if ((normalized.includes('SKILL DEVELOPMENT COURSE') && !normalized.includes('DATA VISUALIZATION') && !normalized.includes('POWER BI') && !normalized.includes('POWERBI') && !normalized.includes('NODE JS') && !normalized.includes('REACT JS') && !normalized.includes('DJANGO')) ||
                normalized.includes('UI DESIGN FLUTTER')) {
                labels.push('Flutter Lab');
            }
            if (normalized.includes('PROJECT STAGE') && (normalized.includes(' I') || normalized.includes(' 1') || normalized.includes('-I') || normalized.includes('-1'))) {
                labels.push('Project Stage-1 Lab');
            }
            const fallbackAcronym = buildSubjectAcronym(subjectName);
            if (fallbackAcronym) {
                labels.push(fallbackAcronym);
            }

            return uniqueSubjectNames(labels);
        }

        function setIndividualSlotValue(card, day, period, value) {
            const slot = getIndividualTimeTableSlots(card).find(function (candidate) {
                return candidate.dataset.day === day && candidate.dataset.period === period;
            });
            if (slot) {
                slot.value = value || '';
                return 1;
            }
            return 0;
        }

        function isVisibleEmptyIndividualSlot(slot) {
            const cell = slot ? slot.closest('td') : null;
            return Boolean(slot && cell && cell.style.display !== 'none' && !slot.value.trim());
        }

        function countIndividualHoursForValue(card, value) {
            const normalizedValue = normalizeSubjectNameForSchedule(value);
            return getIndividualTimeTableSlots(card).reduce(function (total, slot) {
                const cell = slot.closest('td');
                if (!cell || cell.style.display === 'none' || normalizeSubjectNameForSchedule(getComparableSubjectValue(slot.value)) !== normalizedValue) {
                    return total;
                }
                return total + (cell.colSpan && cell.colSpan > 1 ? cell.colSpan : 1);
            }, 0);
        }

        function getSelectionContextLabel(selection) {
            return [
                selection.regulation || 'R22',
                getYearSemLabel(selection.year, selection.semester),
                getBranchDisplayLabel(selection.branch)
            ].filter(Boolean).join(' ');
        }

        function getIndividualRequiredLoads(schedule) {
            const loadMap = new Map();
            normalizeSubjectSelections(schedule.selections || []).forEach(function (selection) {
                const subjectName = (selection.subjectName || '').trim();
                if (!subjectName) {
                    return;
                }
                const shortLabel = getShortSubjectLabel(subjectName);
                const displayValue = getSelectionContextLabel(selection) + ' - ' + shortLabel;
                const key = normalizeSubjectNameForSchedule(displayValue);
                if (loadMap.has(key)) {
                    return;
                }
                loadMap.set(key, {
                    value: displayValue,
                    isLab: isLaboratorySubject(subjectName) || isLaboratorySubject(shortLabel),
                    targetHours: isLaboratorySubject(subjectName) || isLaboratorySubject(shortLabel) ? 2 : 5
                });
            });
            return Array.from(loadMap.values());
        }

        function findEmptyIndividualLabStartSlot(card) {
            const labStartPeriods = ['9:30-10:30', '1:20-2:15'];
            return getIndividualTimeTableSlots(card).find(function (slot) {
                if (!labStartPeriods.includes(slot.dataset.period) || !isVisibleEmptyIndividualSlot(slot)) {
                    return false;
                }
                const cell = slot.closest('td');
                const row = cell ? cell.closest('tr') : null;
                const rowCells = row ? Array.from(row.children) : [];
                const nextCell = rowCells[rowCells.indexOf(cell) + 1];
                const nextSlot = nextCell ? nextCell.querySelector('.individual-timetable-slot') : null;
                return isVisibleEmptyIndividualSlot(nextSlot);
            }) || null;
        }

        function topUpIndividualRequiredLoads(card, schedule) {
            let addedHours = 0;
            getIndividualRequiredLoads(schedule).forEach(function (load) {
                let currentHours = countIndividualHoursForValue(card, load.value);
                while (currentHours < load.targetHours) {
                    if (load.isLab) {
                        const labSlot = findEmptyIndividualLabStartSlot(card);
                        if (!labSlot || !mergeIndividualSlotWithNextPeriod(labSlot, load.value)) {
                            break;
                        }
                        currentHours += 2;
                        addedHours += 2;
                        continue;
                    }

                    const slot = getIndividualTimeTableSlots(card).find(isVisibleEmptyIndividualSlot);
                    if (!slot) {
                        break;
                    }
                    slot.value = load.value;
                    currentHours += 1;
                    addedHours += 1;
                }
            });
            return addedHours;
        }

        function resetIndividualTimeTableMerges(card) {
            getIndividualTimeTableSlots(card).forEach(function (slot) {
                const cell = slot.closest('td');
                if (!cell) {
                    return;
                }
                cell.colSpan = 1;
                cell.style.display = '';
                cell.classList.remove('lab-merged-cell');
                slot.classList.remove('lab-merged-slot');
            });
        }

        function mergeIndividualSlotWithNextPeriod(slot, subjectName) {
            const cell = slot.closest('td');
            const row = cell ? cell.closest('tr') : null;
            if (!cell || !row) {
                return false;
            }

            const cells = Array.from(row.children);
            const currentIndex = cells.indexOf(cell);
            const nextCell = cells[currentIndex + 1];
            if (!nextCell || nextCell.classList.contains('individual-break') || nextCell.style.display === 'none') {
                return false;
            }

            const nextSlot = nextCell.querySelector('.individual-timetable-slot');
            if (!nextSlot) {
                return false;
            }

            slot.value = subjectName;
            nextSlot.value = '';
            cell.colSpan = 2;
            cell.classList.add('lab-merged-cell');
            slot.classList.add('lab-merged-slot');
            nextCell.style.display = 'none';
            return true;
        }

        function restoreIndividualLabMergesFromValues(card) {
            const labStartPeriods = ['9:30-10:30', '1:20-2:15'];
            getIndividualTimeTableSlots(card).forEach(function (slot) {
                const subjectName = (slot.value || '').trim();
                if (
                    !subjectName ||
                    !(
                        (isLaboratoryScheduleValue(subjectName) && labStartPeriods.includes(slot.dataset.period))
                    )
                ) {
                    return;
                }

                mergeIndividualSlotWithNextPeriod(slot, subjectName);
            });
        }

        function getIndividualScheduleLabelsForContext(schedule, context) {
            const labels = [];
            normalizeSubjectSelections(schedule.selections || []).forEach(function (selection) {
                if (getSelectionContextKey(selection) !== context.selectionKey) {
                    return;
                }
                const subjectName = (selection.subjectName || '').trim();
                getScheduleLabelsForSelection(selection).concat([
                    subjectName,
                    getShortSubjectLabel(subjectName)
                ]).forEach(function (label) {
                    if (label) {
                        labels.push(label);
                    }
                });
            });
            return new Set(uniqueSubjectNames(labels).map(function (label) {
                return normalizeSubjectNameForSchedule(label);
            }));
        }

        function populateIndividualCardFromClassSchedule(card, schedule, classContexts) {
            let filledHours = 0;

            resetIndividualTimeTableMerges(card);
            getIndividualTimeTableSlots(card).forEach(function (slot) {
                slot.value = '';
            });

            (classContexts || getClassTimeTableContexts()).forEach(function (context) {
                const normalizedLabels = getIndividualScheduleLabelsForContext(schedule, context);
                if (!normalizedLabels.size) {
                    return;
                }

                context.slots.forEach(function (classSlot) {
                    const subjectName = (classSlot.value || '').trim();
                    if (!subjectName || !normalizedLabels.has(normalizeSubjectNameForSchedule(getComparableSubjectValue(subjectName)))) {
                        return;
                    }

                    const classCell = classSlot.closest('td');
                    const row = classCell ? classCell.closest('tr') : null;
                    const individualSlot = getIndividualTimeTableSlots(card).find(function (candidate) {
                        return candidate.dataset.day === classSlot.dataset.day && candidate.dataset.period === classSlot.dataset.period;
                    });
                    const displayValue = (context.label ? context.label + ' - ' : '') + subjectName;

                    if (!classCell || !row || classCell.colSpan < 2 || !individualSlot) {
                        filledHours += setIndividualSlotValue(card, classSlot.dataset.day, classSlot.dataset.period, displayValue);
                        return;
                    }

                    const rowCells = Array.from(row.children);
                    const nextCell = rowCells[rowCells.indexOf(classCell) + 1];
                    const nextClassSlot = nextCell ? nextCell.querySelector(context.slotSelector || '.timetable-slot') : null;
                    if (nextClassSlot && mergeIndividualSlotWithNextPeriod(individualSlot, displayValue)) {
                        filledHours += 2;
                        return;
                    }

                    filledHours += setIndividualSlotValue(card, classSlot.dataset.day, classSlot.dataset.period, displayValue);
                });
            });

            return filledHours;
        }

        function renderIndividualFacultyTimeTables(selections, classContexts) {
            const schedules = buildIndividualFacultySchedules(selections);
            const cards = ensureIndividualTimeTableCardCount(schedules.length || 1);
            let totalFilledHours = 0;

            if (!schedules.length) {
                const primaryContext = (classContexts && classContexts[0]) || null;
                if (primaryContext && primaryContext.slots) {
                    const primarySlots = primaryContext.slots.filter(function (slot) {
                        const cell = getTimeTableSlotCell(slot);
                        return cell && cell.style.display !== 'none' && slot.value.trim();
                    });
                    if (primarySlots.length) {
                        resetIndividualTimeTableMerges(cards[0]);
                        getIndividualTimeTableSlots(cards[0]).forEach(function (slot) {
                            slot.value = '';
                        });
                        const individualSlots = getIndividualTimeTableSlots(cards[0]);
                        primarySlots.forEach(function (classSlot, index) {
                            if (index < individualSlots.length) {
                                const subjectName = (classSlot.value || '').trim();
                                const displayValue = subjectName ? (primaryContext.label ? primaryContext.label + ' - ' : '') + subjectName : '';
                                individualSlots[index].value = displayValue;
                                totalFilledHours += 1;
                            }
                        });
                        const hoursField = getIndividualTimeTableMetaFields(cards[0]).find(function (field) {
                            return field.id === 'individualTotalHours' || field.getAttribute('aria-label') === 'Number of hours';
                        });
                        if (hoursField) {
                            hoursField.value = String(totalFilledHours);
                        }
                        const title = cards[0].querySelector('.card-title');
                        if (title) {
                            title.textContent = 'Individual Time Table - ' + (primaryContext.label || 'Faculty');
                        }
                        const facultyField = getIndividualTimeTableMetaFields(cards[0]).find(function (field) {
                            return field.id === 'individualFacultyName' || field.getAttribute('aria-label') === 'Faculty Name';
                        });
                        if (facultyField) {
                            facultyField.value = primaryContext.label || '';
                        }
                        return totalFilledHours;
                    }
                }
                generateIndividualTimeTableSlots([], 16, cards[0]);
                getIndividualTimeTableMetaFields(cards[0]).forEach(function (field) {
                    field.value = '';
                });
                return 0;
            }

            schedules.forEach(function (schedule, index) {
                const card = cards[index];
                const metaFields = getIndividualTimeTableMetaFields(card);
                const facultyField = metaFields.find(function (field) {
                    return field.id === 'individualFacultyName' || field.getAttribute('aria-label') === 'Faculty Name';
                });
                const hoursField = metaFields.find(function (field) {
                    return field.id === 'individualTotalHours' || field.getAttribute('aria-label') === 'Number of hours';
                });
                const filledHours = populateIndividualCardFromClassSchedule(card, schedule, classContexts);
                const title = card.querySelector('.card-title');

                if (facultyField) {
                    facultyField.value = [schedule.facultyName, schedule.employeeCode].filter(Boolean).join(' - ');
                }
                if (hoursField) {
                    hoursField.value = String(filledHours);
                }
                if (title) {
                    title.textContent = 'Individual Time Table - ' + (schedule.facultyName || schedule.employeeCode || 'Faculty');
                }
                totalFilledHours += filledHours;
            });

            return totalFilledHours;
        }

        function uniqueSubjectNames(subjectNames) {
            return Array.from(new Set((subjectNames || []).map(function (subjectName) {
                return (subjectName || '').trim();
            }).filter(Boolean)));
        }

        function normalizeSubjectNameForSchedule(subjectName) {
            return String(subjectName || '')
                .trim()
                .toUpperCase()
                .replace(/&/g, 'AND')
                .replace(/\s+/g, ' ');
        }

        function buildStandardSubjectLookup(subjectNames) {
            const standardSubjects = {
                daa: 'DAA',
                acd: 'ACD',
                es: 'ES',
                dm: 'DM',
                ddb: 'DDB',
                compilerLab: 'CD Lab',
                embeddedLab: 'ES Lab',
                dataMiningLab: 'Data Mining Lab',
                sdc: 'Flutter Lab'
            };
            const aliases = {
                daa: ['DESIGN AND ANALYSIS OF ALGORITHMS'],
                acd: ['AUTOMATA AND COMPILER DESIGN'],
                es: ['EMBEDDED SYSTEMS'],
                dm: ['DATA MINING'],
                ddb: ['DISTRIBUTED DATABASES'],
                compilerLab: ['COMPILER DESIGN LABORATORY', 'COMPILER DESIGN LAB'],
                embeddedLab: ['EMBEDDED SYSTEMS LABORATORY', 'EMBEDDED SYSTEMS LAB'],
                dataMiningLab: ['DATA MINING LABORATORY', 'DATA MINING LAB'],
                sdc: ['SKILL DEVELOPMENT COURSE (UI DESIGN FLUTTER)', 'UI DESIGN FLUTTER']
            };
            const allSubjectNames = uniqueSubjectNames(subjectNames);
            const availableSubjects = allSubjectNames.map(function (subjectName) {
                return {
                    original: subjectName,
                    normalized: normalizeSubjectNameForSchedule(subjectName)
                };
            });
            const usedSubjectNames = new Set();
            const lookup = {
                daa: standardSubjects.daa,
                acd: standardSubjects.acd,
                es: standardSubjects.es,
                dm: standardSubjects.dm,
                ddb: standardSubjects.ddb,
                compilerLab: standardSubjects.compilerLab,
                embeddedLab: standardSubjects.embeddedLab,
                dataMiningLab: standardSubjects.dataMiningLab,
                sdc: standardSubjects.sdc,
                library: 'LIBRARY',
                sports: 'SPORTS',
                mentoring: 'MENTORING'
            };

            Object.keys(aliases).forEach(function (key) {
                const matched = availableSubjects.find(function (subject) {
                    return aliases[key].some(function (alias) {
                        return subject.normalized === alias || subject.normalized.includes(alias);
                    });
                });
                if (matched) {
                    lookup[key] = standardSubjects[key];
                    usedSubjectNames.add(matched.original);
                }
            });

            const theoryKeys = ['daa', 'acd', 'es', 'dm', 'ddb'];
            const labKeys = ['compilerLab', 'embeddedLab', 'dataMiningLab', 'sdc'];
            const remainingTheorySubjects = allSubjectNames.filter(function (subjectName) {
                return !usedSubjectNames.has(subjectName) && !isLaboratorySubject(subjectName);
            });
            const remainingLabSubjects = allSubjectNames.filter(function (subjectName) {
                return !usedSubjectNames.has(subjectName) && isLaboratorySubject(subjectName);
            });

            theoryKeys.forEach(function (key) {
                if (!lookup[key] && remainingTheorySubjects.length) {
                    lookup[key] = getShortSubjectLabel(remainingTheorySubjects.shift());
                }
            });

            labKeys.forEach(function (key) {
                if (!lookup[key] && remainingLabSubjects.length) {
                    lookup[key] = getShortSubjectLabel(remainingLabSubjects.shift());
                }
            });

            return lookup;
        }

        function generateClassTimeTableSlots(subjectNames) {
            const subjectLookup = buildStandardSubjectLookup(subjectNames);
            const weeklyPlan = {
                MON: ['ddb', 'acd', 'daa', 'embeddedLab', null, 'dm'],
                TUE: ['dataMiningLab', null, 'acd', 'dm', 'daa', 'es'],
                WED: ['daa', 'es', 'dm', 'acd', 'ddb', 'mentoring'],
                THU: ['es', 'acd', 'daa', 'sdc', null, 'ddb'],
                FRI: ['dm', 'es', 'ddb', 'compilerLab', null, 'library'],
                SAT: ['acd', 'dm', 'es', 'daa', 'ddb', 'sports']
            };
            const counts = {};
            const labDaysUsed = new Set();
            let labMergedCount = 0;

            timeTableSlots.forEach(function (slot) {
                slot.value = '';
            });

            Object.keys(weeklyPlan).forEach(function (day) {
                const dailySubjects = new Set();
                weeklyPlan[day].forEach(function (subjectKey, periodIndex) {
                    if (!subjectKey) {
                        return;
                    }

                    const subjectName = subjectLookup[subjectKey];
                    if (!subjectName) {
                        return;
                    }

                    const slot = getClassSlot(day, periodOrder[periodIndex]);
                    if (!slot) {
                        return;
                    }

                    if (isLaboratorySubject(subjectName)) {
                        if ((periodIndex !== 0 && periodIndex !== 3) || normalizeClassValue(day) === 'SAT' || labDaysUsed.has(day)) {
                            return;
                        }
                        if (mergeSlotWithNextPeriod(slot, subjectName)) {
                            counts[subjectName] = (counts[subjectName] || 0) + 2;
                            labDaysUsed.add(day);
                            labMergedCount += 1;
                        }
                        return;
                    }

                    if (dailySubjects.has(subjectName)) {
                        return;
                    }

                    slot.value = subjectName;
                    dailySubjects.add(subjectName);
                    counts[subjectName] = (counts[subjectName] || 0) + 1;
                });
            });

            return {
                counts: counts,
                labMergedCount: labMergedCount,
                totalHours: Object.keys(counts).reduce(function (total, subjectName) {
                    return total + counts[subjectName];
                }, 0)
            };
        }

        function findSyllabusSubjectByCode(subjects, code) {
            return (subjects || []).find(function (subject) {
                return (subject.code || '').toUpperCase() === (code || '').toUpperCase();
            }) || null;
        }

        function chooseSubjectFromCodes(subjects, selectedCodes, allowedCodes) {
            const normalizedAllowed = allowedCodes.map(function (code) {
                return code.toUpperCase();
            });
            const selectedMatch = selectedCodes.find(function (code) {
                return normalizedAllowed.includes((code || '').toUpperCase());
            });
            return findSyllabusSubjectByCode(subjects, selectedMatch) || findSyllabusSubjectByCode(subjects, allowedCodes[0]);
        }

        function resolveClassSubjectsForTimeTable(syllabusSubjects, selections, fallbackSubjectNames) {
            const subjects = Array.isArray(syllabusSubjects) ? syllabusSubjects : [];
            return subjects.length
                ? uniqueSubjectNames(subjects.map(function (subject) { return subject.name; }))
                : uniqueSubjectNames(fallbackSubjectNames);
        }

        function getRequiredHourSummary(classSelections, context) {
            const assignments = buildClassAssignments(classSelections, context);
            const theoryAssignments = assignments.filter(function (assignment) {
                return !assignment.isLab && !assignment.isActivity;
            });
            const labAssignments = assignments.filter(function (assignment) {
                return assignment.isLab;
            });
            const activityAssignments = assignments.filter(function (assignment) {
                return assignment.isActivity;
            });
            const targetHours = function (items) {
                return items.reduce(function (total, assignment) {
                    return total + (assignment.targetHours || 0);
                }, 0);
            };

            return {
                theoryCount: theoryAssignments.length,
                labCount: labAssignments.length,
                activityCount: activityAssignments.length,
                theoryHours: targetHours(theoryAssignments),
                labHours: targetHours(labAssignments),
                activityHours: targetHours(activityAssignments),
                totalHours: targetHours(assignments)
            };
        }

        function generateTimeTableFromSubjectSelection() {
            const currentPayload = getSubjectSelectionPayload();
            let selections = getStoredSubjectSelections();

            if (!selections.length && currentPayload.facultyName && currentPayload.employeeCode && currentPayload.subjectName) {
                selections = [currentPayload];
                storeSubjectSelections(selections);
                renderSubjectSelectionPreview(selections);
            }

            if (!selections.length) {
                setStatus(subjectSelectionStatus, 'Add at least one faculty before generating timetable', 'warning');
                return;
            }

            const payload = choosePrimarySubjectSelection(selections) || selections[0];

            const hasExistingTimetable = timeTableSlots.some(function (slot) {
                return slot.value.trim();
            }) || getIndividualTimeTableSlots().some(function (slot) {
                return slot.value.trim();
            });

            if (hasExistingTimetable && !confirm('Generate timetable from this subject selection and replace existing timetable entries?')) {
                return;
            }

            storeSubjectSelections(selections);
            renderSubjectSelectionPreview(selections);
            resetClassTimeTableMerges();

            if (subjectSelectionFields.regulation) {
                subjectSelectionFields.regulation.value = payload.regulation || subjectSelectionFields.regulation.value || 'R22';
            }
            timeTableBranchField.value = payload.branch || timeTableBranchField.value;
            timeTableYearField.value = payload.year || timeTableYearField.value;
            timeTableSemesterField.value = payload.semester || timeTableSemesterField.value;
            renderCourseReference(selections);

            const classContexts = getClassTimeTableContexts(selections);
            const timetableSelections = getSelectionsForClassContexts(selections, classContexts);

             loadSyllabusSubjects(payload.subjectCode).then(function (data) {
                 classContexts.forEach(function (context) {
                     resetClassTimeTableMerges(context.slots);
                     (context.slots || []).forEach(function (slot) { slot.value = ''; });
                 });
                 const facultyOccupancyMap = createFacultyOccupancyMap();
                 const labRoomOccupancyMap = createLabRoomOccupancyMap();
                 prePopulateOccupancyMapsFromExistingData(facultyOccupancyMap, labRoomOccupancyMap);
                  const classGeneration = classContexts.reduce(function (summary, context) {
                      const contextSelections = getSelectionsForClassContext(selections, context);
                      const generated = generateClassTimeTableSlotsForContext(
                          context,
                          contextSelections,
                          facultyOccupancyMap,
                          labRoomOccupancyMap
                      );
                      // Reserve this context's placed faculty/room periods into the shared
                      // occupancy maps so subsequent contexts (e.g. 2-1 vs 3-1) cannot
                      // double-book the same faculty member or lab room at the same slot.
                      prePopulateOccupancyMapsFromExistingData(facultyOccupancyMap, labRoomOccupancyMap);
                      const contextHours = countClassContextHours(context);
                     summary.contexts.push({
                         label: context.label,
                         hours: contextHours,
                         requiredHours: isR22ThreeTwoAIMLContext(context) ? 36 : (getRequiredHourSummary(contextSelections, context).totalHours || 36)
                     });
                     summary.labMergedCount += generated.labMergedCount || 0;
                     summary.totalHours += contextHours;
                     return summary;
                 }, { labMergedCount: 0, totalHours: 0, contexts: [] });
                  const repairSummary = applyTimeTableRequirementRepairs(classContexts, selections);
                  const finalLabRoomRepairs = repairAllClassLabRoomConflicts(classContexts, selections);
                  repairSummary.labRoomConflicts += finalLabRoomRepairs;
                  repairSummary.total += finalLabRoomRepairs;
                   const finalBlankFills = fillAllClassBlankSlots(classContexts, selections);
                   repairSummary.filledBlankSlots += finalBlankFills;
                   repairSummary.total += finalBlankFills;
                   const finalResourceRepairs = repairAllTimetableResourceConflicts(classContexts, selections);
                   repairSummary.labRoomConflicts += finalResourceRepairs.labRoom;
                   repairSummary.facultyConflicts += finalResourceRepairs.faculty;
                  repairSummary.morningTheoryCoverage = repairMorningTheoryCoverage(classContexts, selections);
                   const fixedAIMLSectionPlan = enforceR22ThreeTwoAIMLPlans(classContexts, selections);
                   repairSummary.fixedLayouts += fixedAIMLSectionPlan;
                   repairSummary.total += fixedAIMLSectionPlan;
                   if (fixedAIMLSectionPlan) {
                       syncIndividualTimeTablesWithMainTables(selections, classContexts);
                   }
                   classGeneration.contexts.forEach(function (contextSummary, index) {
                       contextSummary.hours = countClassContextHours(classContexts[index]);
                   });
                 const fixedAIMLSectionCount = classContexts.filter(isR22ThreeTwoAIMLContext).length;
                 const labMergedCount = Math.max(classGeneration.labMergedCount || 0, fixedAIMLSectionCount * 4);
                 const classTotalHours = classGeneration.contexts.reduce(function (total, contextSummary) {
                     return total + (contextSummary.hours || 0);
                 }, 0);
                 const incompleteContexts = classGeneration.contexts.filter(function (contextSummary) {
                     return contextSummary.hours < Math.min(contextSummary.requiredHours || 36, 36);
                 });
                 const requiredSummary = classContexts.reduce(function (summary, context) {
                     const required = isR22ThreeTwoAIMLContext(context)
                         ? { theoryCount: 5, labCount: 4, activityCount: 3, theoryHours: 25, labHours: 8, activityHours: 3, totalHours: 36 }
                         : getRequiredHourSummary(getSelectionsForClassContext(selections, context), context);
                     summary.theoryCount += required.theoryCount;
                     summary.labCount += required.labCount;
                     summary.activityCount += required.activityCount;
                     summary.theoryHours += required.theoryHours;
                     summary.labHours += required.labHours;
                     summary.activityHours += required.activityHours;
                     summary.totalHours += required.totalHours;
                     return summary;
                 }, { theoryCount: 0, labCount: 0, activityCount: 0, theoryHours: 0, labHours: 0, activityHours: 0, totalHours: 0 });
                  normalizeAllTimeTableSlotValues();
                  saveTimeTableData();

                  if (syllabusSubjectSelect && payload.subjectCode) {
                      syllabusSubjectSelect.value = payload.subjectCode;
                  }
                  markTimeTableDirty();
                 setStatus(
                     timeTableStatus,
                     'Timetable generated with ' + classTotalHours + ' class hours; required load is ' +
                     requiredSummary.theoryCount + ' theory (' + requiredSummary.theoryHours + ' hours) + ' +
                     requiredSummary.labCount + ' lab (' + requiredSummary.labHours + ' hours) + ' +
                     requiredSummary.activityCount + ' activity (' + requiredSummary.activityHours + ' hours) = ' +
                     requiredSummary.totalHours + ' hours' +
                     (labMergedCount ? '; laboratory subjects are merged into two-hour blocks' : '') +
                     (repairSummary.sameHourRepeats ? '; same-hour repeated subjects were corrected' : '') +
                     (repairSummary.facultyConflicts ? '; faculty double-bookings were resolved' : '') +
                     (repairSummary.labRoomConflicts ? '; same-room lab clashes were corrected across II-II, III-II, and IV-II' : '') +
                     (repairSummary.addedAIMLOSLab ? '; R25 II-II CSE (AI&ML) full load was filled' : '') +
                     (repairSummary.projectStageLabs ? '; IV-II project lab was added' : '') +
                     (repairSummary.filledBlankSlots ? '; empty slots were filled where possible' : '') +
                     (repairSummary.movedActivities ? '; activity hours were moved to the last hours' : '') +
                     (repairSummary.annotatedLabRooms ? '; lab room numbers were added to lab slots' : '') +
                     (incompleteContexts.length
                         ? '; warning: incomplete 36-hour load for ' + incompleteContexts.map(function (contextSummary) {
                             return contextSummary.label + ' (' + contextSummary.hours + ' hours)';
                         }).join(', ')
                         : '; every generated class timetable has 36 hours filled') +
                     '; short subject names are used in the main timetable',
                     incompleteContexts.length ? 'warning' : 'success'
                 );
                  setStatus(subjectSelectionStatus, 'Time Table generated from ' + selections.length + ' available faculty selection(s)', 'success');
                  setTimeout(function () {
                      switchToTimeTableTab();
                  }, 50);
              }).catch(function (error) {
                  console.error(error);
                  setStatus(timeTableStatus, 'Error generating timetable: ' + (error.message || error), 'warning');
                  setTimeout(function () {
                      switchToTimeTableTab();
                  }, 50);
              });
        }

        document.getElementById('addBtn').addEventListener('click', addRowsFromRange);
        document.getElementById('saveBtn').addEventListener('click', saveTeachingPlan);
        document.getElementById('deleteBtn').addEventListener('click', deleteTeachingPlan);

        lessonPlanBody.addEventListener('input', function (event) {
            if (event.target.classList.contains('classes-taken-input')) {
                updateLessonTotals();
            }
            markLessonDirty();
        });

        Object.values(lessonHeaderFields).forEach(function (field) {
            field.addEventListener('input', markLessonDirty);
        });

        document.getElementById('fromDate').addEventListener('change', markLessonDirty);
        document.getElementById('toDate').addEventListener('change', markLessonDirty);

        document.getElementById('addStudentsBtn').addEventListener('click', regenerateStudentSheet);
        document.getElementById('evalSaveBtn').addEventListener('click', saveEvaluationData);
        document.querySelectorAll('.eval-section-save-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const sheet = btn.getAttribute('data-sheet');
                if (sheet) saveEvaluationSheetData(sheet);
            });
        });
        document.getElementById('evalClearBtn').addEventListener('click', clearEvaluationData);
        const evaluationDownloadModal = document.getElementById('evaluationDownloadModal');
        // Keep the modal above Bootstrap's body-level backdrop and outside .exam-shell's stacking context.
        evaluationDownloadModal.classList.add('exam-branch-page');
        document.body.appendChild(evaluationDownloadModal);
        document.getElementById('evalDownloadBtn').addEventListener('click', function () {
            if (!window.bootstrap || !window.bootstrap.Modal) {
                setStatus(evaluationSaveStatus, 'The evaluation download dialog is unavailable', 'warning');
                return;
            }
            document.getElementById('evaluationDownloadSheet').value = activeEvaluationSheet;
            window.bootstrap.Modal.getOrCreateInstance(evaluationDownloadModal).show();
        });
        document.getElementById('evaluationDownloadForm').addEventListener('submit', function (event) {
            event.preventDefault();
            downloadEvaluationExcel(document.getElementById('evaluationDownloadSheet').value);
        });
        Object.values(evaluationSubjectNameMap).forEach(function (input) {
            if (input) input.addEventListener('input', markEvaluationDirty);
        });
        evaluationSheetSelect.addEventListener('change', function () {
            saveEvaluationData();
            activeEvaluationSheet = evaluationSheetSelect.value;
            loadEvaluationData();
            updateAllEvaluationAverages();
        });
        document.addEventListener('click', function (event) {
            const button = event.target.closest('.timetable-edit-btn');
            if (!button) return;
            const enabled = button.dataset.editing !== 'true';
            const scope = button.dataset.editScope;
            let root = null;
            if (scope === 'main') root = document.getElementById('timeTableGrid');
            if (scope === 'empty') root = button.closest('[data-empty-timetable-card]');
            if (scope === 'individual') root = button.closest('[data-individual-timetable-card]');
            setTimetableFieldsEditable(root, enabled);
            button.dataset.editing = String(enabled);
            button.innerHTML = enabled
                ? '<i class="fas fa-check me-2"></i>Done Editing'
                : (scope === 'individual' ? '<i class="fas fa-edit me-2"></i>Edit Individual Time Table' : '<i class="fas fa-edit me-2"></i>Edit Timetable');
            if (!enabled) saveTimeTableData();
        });
        document.getElementById('timeTableSaveBtn').addEventListener('click', saveTimeTableData);
        document.getElementById('timeTableClearBtn').addEventListener('click', clearTimeTableData);
        document.getElementById('labTimeTableClearBtn').addEventListener('click', clearTimeTableData);
        subjectSelectionForm.addEventListener('submit', saveSubjectSelection);
        document.getElementById('subjectSelectionAddFacultyBtn').addEventListener('click', addFacultySubjectSelection);
        document.getElementById('subjectSelectionAddBtn').addEventListener('click', generateTimeTableFromSubjectSelection);
        document.getElementById('subjectSelectionClearBtn').addEventListener('click', clearSubjectSelection);
        subjectSelectionPreviewBody.addEventListener('click', function (event) {
            const deleteButton = event.target.closest('.subject-selection-delete-btn');
            if (!deleteButton) {
                return;
            }
            deleteFacultySubjectSelection(parseInt(deleteButton.dataset.index, 10));
        });

        // Attach event listeners to all marks bodies
        Object.keys(marksBodyMap).forEach(function(sheetNum) {
            if (marksBodyMap[sheetNum]) {
                marksBodyMap[sheetNum].addEventListener('input', function (event) {
                    if (event.target.closest('tr')) {
                        if (sheetNum === '1' && event.target.classList.contains('roll-no')) {
                            const evaluationOneRows = Array.from(marksBodyMap['1'].querySelectorAll('tr'));
                            const rowIndex = evaluationOneRows.indexOf(event.target.closest('tr'));
                            const evaluationThreeRows = marksBodyMap['3']
                                ? Array.from(marksBodyMap['3'].querySelectorAll('tr')) : [];
                            const evaluationThreeRollInput = evaluationThreeRows[rowIndex]
                                ? evaluationThreeRows[rowIndex].querySelector('.roll-no') : null;
                            if (evaluationThreeRollInput) evaluationThreeRollInput.value = event.target.value;
                        }
                        activeEvaluationSheet = sheetNum;
                        evaluationSheetSelect.value = sheetNum;
                        recalculateEvaluationRow(event.target.closest('tr'));
                        updateAttendanceGrades();
                        updateGradeSummary();
                        updateEvaluationMetrics();
                        updateAllEvaluationAverages();
                        markEvaluationDirty();
                    }
                });
            }
        });

        document.getElementById('studentCount').addEventListener('input', markEvaluationDirty);

        timeTableSlots.forEach(function (slot) {
            slot.addEventListener('input', function () {
                markTimeTableDirty();
                persistManualTimeTableEdit();
            });
            slot.addEventListener('change', function () {
                slot.value = normalizeTimeTableDisplayValue(slot.value);
                const selections = getStoredSubjectSelections();
                const classContexts = getClassTimeTableContexts(selections);
                syncIndividualTimeTablesWithMainTables(selections, classContexts);
                normalizeAllTimeTableSlotValues();
                saveTimeTableData();
            });
        });

        mainTimeTableDownloadButtons.forEach(function (button) {
            button.addEventListener('click', function () {
                const selections = getStoredSubjectSelections();
                const classContexts = getClassTimeTableContexts(selections);
                applyTimeTableRequirementRepairs(classContexts, selections);
                repairAllClassLabRoomConflicts(classContexts, selections);
                repairAllFacultyConflicts(classContexts, selections);
                fillAllClassBlankSlots(classContexts, selections);
                repairAllTimetableResourceConflicts(classContexts, selections);
                const fixedAIMLSectionPlan = enforceR22ThreeTwoAIMLPlans(classContexts, selections);
                if (fixedAIMLSectionPlan) {
                    saveTimeTableData();
                }
                syncIndividualTimeTablesWithMainTables(selections, classContexts);
                normalizeAllTimeTableSlotValues();
                downloadMainTimeTableExcel(button);
            });
        });

        getEmptyTimeTableSlots().forEach(function (slot) {
            slot.addEventListener('input', function () {
                markTimeTableDirty();
                persistManualTimeTableEdit();
            });
            slot.addEventListener('change', function () {
                slot.value = normalizeTimeTableDisplayValue(slot.value);
                const selections = getStoredSubjectSelections();
                const classContexts = getClassTimeTableContexts(selections);
                syncIndividualTimeTablesWithMainTables(selections, classContexts);
                normalizeAllTimeTableSlotValues();
                saveTimeTableData();
            });
        });

        timeTableMetaFields.forEach(function (field) {
            field.addEventListener('input', markTimeTableDirty);
            field.addEventListener('change', function () {
                markTimeTableDirty();
                if (field === timeTableYearField || field === timeTableSemesterField || field === timeTableBranchField) {
                    loadSyllabusSubjects();
                }
            });
        });

        if (individualTimeTableContainer) {
            individualTimeTableContainer.addEventListener('click', function (event) {
                const downloadButton = event.target.closest('[data-download-individual-timetable]');
                if (downloadButton) {
                    downloadIndividualTimeTableExcel(downloadButton.closest('[data-individual-timetable-card]'));
                }
            });
            individualTimeTableContainer.addEventListener('input', function (event) {
                if (
                    event.target.classList.contains('individual-timetable-slot') ||
                    event.target.classList.contains('individual-timetable-meta-input')
                ) {
                    markTimeTableDirty();
                    if (event.target.classList.contains('individual-timetable-slot')) {
                        const card = event.target.closest('[data-individual-timetable-card]');
                        if (card) saveTimeTableData();
                    }
                    saveTimeTableData();
                }
            });
            individualTimeTableContainer.addEventListener('change', function (event) {
                if (event.target.classList.contains('individual-timetable-slot')) {
                    event.target.value = normalizeTimeTableDisplayValue(event.target.value);
                    const selections = getStoredSubjectSelections();
                    const classContexts = getClassTimeTableContexts(selections);
                    syncClassTimeTablesFromIndividualCard(event.target.closest('[data-individual-timetable-card]'), selections, classContexts);
                    repairAllClassTimeTableSameHourRepeats(classContexts);
                    repairAllFacultyConflicts(classContexts, selections);
                    repairAllClassLabRoomConflicts(classContexts, selections);
                    enforceActivitiesLastHours(classContexts);
                    repairAllClassLabRoomConflicts(classContexts, selections);
                    repairAllFacultyConflicts(classContexts, selections);
                    fillAllClassBlankSlots(classContexts, selections);
                    repairAllTimetableResourceConflicts(classContexts, selections);
                    syncIndividualTimeTablesWithMainTables(selections, classContexts);
                    normalizeAllTimeTableSlotValues();
                    saveTimeTableData();
                }
            });
        }

        Object.values(subjectSelectionFields).forEach(function (field) {
            field.addEventListener('input', markSubjectSelectionDirty);
            field.addEventListener('change', function () {
                markSubjectSelectionDirty();
                if (field === subjectSelectionFields.regulation || field === subjectSelectionFields.year || field === subjectSelectionFields.semester || field === subjectSelectionFields.branch || field === subjectSelectionFields.section) {
                    loadSubjectSelectionSubjects();
                }
            });
        });

        var syncingMetaFields = false;

        function syncMetaAcrossTabs(sourceId) {
            if (syncingMetaFields) return;
            syncingMetaFields = true;

            var sourceField = document.getElementById(sourceId);
            if (!sourceField || !sourceField.value) {
                syncingMetaFields = false;
                return;
            }

            var value = sourceField.value;
            var targets = [];
            if (sourceId === 'subjectSelectionBranch') {
                targets = ['timeTableBranch', 'lessonBranch'];
            } else if (sourceId === 'subjectSelectionYear') {
                targets = ['timeTableYear', 'lessonYear'];
            } else if (sourceId === 'subjectSelectionSemester') {
                targets = ['timeTableSemester', 'lessonSemester'];
            } else if (sourceId === 'timeTableBranch') {
                targets = ['subjectSelectionBranch', 'lessonBranch'];
            } else if (sourceId === 'timeTableYear') {
                targets = ['subjectSelectionYear', 'lessonYear'];
            } else if (sourceId === 'timeTableSemester') {
                targets = ['subjectSelectionSemester', 'lessonSemester'];
            } else if (sourceId === 'lessonBranch') {
                targets = ['subjectSelectionBranch', 'timeTableBranch'];
            } else if (sourceId === 'lessonYear') {
                targets = ['subjectSelectionYear', 'timeTableYear'];
            } else if (sourceId === 'lessonSemester') {
                targets = ['subjectSelectionSemester', 'timeTableSemester'];
            }

            targets.forEach(function(targetId) {
                var targetField = document.getElementById(targetId);
                if (targetField && targetField.value !== value) {
                    targetField.value = value;
                }
            });

            if (sourceId.startsWith('timeTable') || sourceId.startsWith('subjectSelection')) {
                loadSyllabusSubjects();
                loadSubjectSelectionSubjects();
            }

            syncingMetaFields = false;
        }

        ['subjectSelectionBranch', 'subjectSelectionYear', 'subjectSelectionSemester', 'timeTableBranch', 'timeTableYear', 'timeTableSemester', 'lessonBranch', 'lessonYear', 'lessonSemester'].forEach(function(fieldId) {
            var field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('change', function() {
                    syncMetaAcrossTabs(fieldId);
                });
            }
        });

        if (syllabusSubjectSelect) {
            syllabusSubjectSelect.addEventListener('change', function () {
                const selectedOption = syllabusSubjectSelect.options[syllabusSubjectSelect.selectedIndex];
                if (!selectedOption || !selectedOption.value) {
                    return;
                }
                useSubjectInLessonPlan({
                    code: selectedOption.value,
                    name: selectedOption.dataset.name || ''
                });
                setStatus(lessonPlanStatus, 'Subject selected from syllabus', 'success');
            });
        }

        loadTeachingPlan();
        let savedDynamicEvaluationSheets = [];
        try {
            savedDynamicEvaluationSheets = JSON.parse(localStorage.getItem('examBranchDynamicEvaluationSheets') || '[]');
        } catch (error) {
            console.error('Could not restore additional evaluation sheets', error);
        }
        savedDynamicEvaluationSheets.forEach(function (sheet) {
            createAdditionalEvaluationSheet(sheet.count || 50, sheet.sheetNumber);
        });
        Object.keys(marksBodyMap).forEach(function (sheetNum) {
            activeEvaluationSheet = sheetNum;
            loadEvaluationData();
        });
        activeEvaluationSheet = '1';
        evaluationSheetSelect.value = '1';
        document.getElementById('studentCount').value = String(defaultEvaluationRollNumbers.length);
        loadTimeTableData();
        initializeTimetableEditState();
        loadSubjectSelection();
        // Persist the default Friday SPORTS and Saturday LIBRARY hours on first visit.
        if (!localStorage.getItem(timeTableStorageKey)) {
            saveTimeTableData();
        }

        var savedSelections = getStoredSubjectSelections();
        if (savedSelections.length > 0) {
            var firstSelection = savedSelections[0];
            if (timeTableBranchField && firstSelection.branch) timeTableBranchField.value = firstSelection.branch;
            if (timeTableYearField && firstSelection.year) timeTableYearField.value = firstSelection.year;
            if (timeTableSemesterField && firstSelection.semester) timeTableSemesterField.value = firstSelection.semester;
            if (syllabusSubjectSelect && firstSelection.subjectCode) syllabusSubjectSelect.value = firstSelection.subjectCode;
        }

        loadSyllabusSubjects();
        renderAllTimeTableLoadSummaries();
        window.setTimeout(function () {
            const hasSavedTimeTable = Boolean(localStorage.getItem(timeTableStorageKey));
            const hasSelections = getStoredSubjectSelections().length > 0;
            const selections = getStoredSubjectSelections();
            const classContexts = getClassTimeTableContexts(selections);
             const repairSummary = applyTimeTableRequirementRepairs(classContexts, selections);
             const finalLabRoomRepairs = repairAllClassLabRoomConflicts(classContexts, selections);
             repairSummary.labRoomConflicts += finalLabRoomRepairs;
             repairSummary.total += finalLabRoomRepairs;
             const finalFacultyRepairs = repairAllFacultyConflicts(classContexts, selections);
             repairSummary.facultyConflicts += finalFacultyRepairs;
             repairSummary.total += finalFacultyRepairs;
             const finalBlankFills = fillAllClassBlankSlots(classContexts, selections);
             repairSummary.filledBlankSlots += finalBlankFills;
             repairSummary.total += finalBlankFills;
             const finalResourceRepairs = repairAllTimetableResourceConflicts(classContexts, selections);
             repairSummary.facultyConflicts += finalResourceRepairs.faculty;
             repairSummary.labRoomConflicts += finalResourceRepairs.labRoom;
             repairSummary.total += finalResourceRepairs.faculty + finalResourceRepairs.labRoom;
             const fixedAIMLSectionPlan = enforceR22ThreeTwoAIMLPlans(classContexts, selections);
             repairSummary.fixedLayouts += fixedAIMLSectionPlan;
             repairSummary.total += fixedAIMLSectionPlan;
             if (repairSummary.total) {
                 syncIndividualTimeTablesWithMainTables(selections, classContexts);
             }
            if (repairSummary.total) {
                saveTimeTableData();
                const statusMessage = repairSummary.fixedLayouts
                    ? 'R22 III-II CSE (AI&ML) Sections A and B were updated and saved with 36 hours each'
                    : repairSummary.facultyConflicts
                        ? 'Faculty double-bookings were resolved and saved'
                        : repairSummary.labRoomConflicts
                            ? 'Same-room lab clashes were corrected and saved'
                            : repairSummary.projectStageLabs
                                ? 'IV-II project lab was added and saved'
                                : repairSummary.filledBlankSlots
                                    ? 'Empty timetable slots were filled and saved'
                                    : repairSummary.movedActivities
                                        ? 'Activity hours were moved to the last hours and saved'
                                        : repairSummary.annotatedLabRooms
                                            ? 'Lab room numbers were added and saved'
                                            : 'Same-hour repeated subjects were corrected and saved';
                setStatus(
                    timeTableStatus,
                    statusMessage,
                    'success'
                );
            }
            renderAllTimeTableLoadSummaries();
        }, 500);
        const labTimeTableTabButton = document.getElementById('lab-timetable-tab');
        const timeTableTabButton = document.getElementById('timetable-tab');
        if (timeTableTabButton) {
            timeTableTabButton.addEventListener('shown.bs.tab', function () {
                const selections = getStoredSubjectSelections();
                const classContexts = getClassTimeTableContexts(selections);
                const fixedAIMLSectionPlan = enforceR22ThreeTwoAIMLPlans(classContexts, selections);
                if (fixedAIMLSectionPlan) {
                    syncIndividualTimeTablesWithMainTables(selections, classContexts);
                    saveTimeTableData();
                    setStatus(timeTableStatus, 'R22 III-II CSE (AI&ML) Section A and B timetables updated and saved with 36 hours each', 'success');
                }
                renderAllTimeTableLoadSummaries();
            });
        }

        if (labTimeTableTabButton) {
            labTimeTableTabButton.addEventListener('shown.bs.tab', function () {
                const selections = getStoredSubjectSelections();
                const classContexts = getClassTimeTableContexts(selections);
                updateLabTimeTable(selections, classContexts);
            });
        }

        })();
    