import fs from 'node:fs';
import path from 'node:path';
import { buildSimulatorSpec, buildWorkingSteps } from './coa_working_steps.mjs';

const projectRoot = path.resolve(process.argv[2] || path.join(import.meta.dirname, '..'));
const file = path.join(projectRoot, 'static', 'academics', 'coa-diagrams', 'manifest.json');
const manifest = JSON.parse(fs.readFileSync(file, 'utf8'));
manifest.figures = manifest.figures.map(figure => ({ ...figure, working_steps: buildWorkingSteps(figure), simulator: buildSimulatorSpec(figure) }));
fs.writeFileSync(file, JSON.stringify(manifest, null, 2));
console.log(`Added diagram-specific working steps to ${manifest.figures.length} COA figures.`);
