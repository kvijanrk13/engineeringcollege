const step = (title, text, x, y, scale = 1.24, tx = 0, ty = 0) => ({ title, text, x, y, scale, tx, ty });

/** Build a diagram-specific teaching sequence from its title, caption, and chapter. */
export function buildWorkingSteps(figure) {
  const subject = figure.topic.replace(/[.;:]$/, '');
  const words = `${figure.topic} ${figure.caption} ${figure.chapter_title}`.toLowerCase();
  const sequence = (input, action, transfer, result) => [
    step('1. Identify the inputs', `${input} In Figure ${figure.figure_number}, first locate every labelled input and control entering ${subject}.`, 18, 45, 1.22, 11),
    step('2. Activate the operation', `${action} The active labels determine which path or component performs work.`, 40, 48, 1.3, 5),
    step('3. Trace the working path', `${transfer} Follow the arrows and intermediate labels in their operating order.`, 66, 52, 1.3, -7),
    step('4. Verify the output', `${result} Relate the final value or state back to the purpose of ${subject}.`, 86, 55, 1.2, -12),
  ];

  if (/truth table|map|karnaugh|boolean|logic function/.test(words)) return sequence(
    'Read the input combinations, minterms, or variables.',
    'Evaluate the Boolean condition for each combination or group adjacent 1-cells in powers of two.',
    'Convert each valid row or group into its product or sum term, eliminating variables that change within a group.',
    'Combine the terms and compare the simplified expression with the output column or mapped cells.'
  );
  if (/flip-flop|counter|shift register|sequence detector/.test(words)) return sequence(
    'Identify clock, set/reset, data inputs, and the present-state outputs.',
    'At the active clock edge, evaluate the excitation inputs and the device characteristic equation.',
    'Transfer the computed next state through each stage; feedback determines the following clock cycle.',
    'Read the new state or count and verify it against the state sequence or timing waveform.'
  );
  if (/adder|subtractor|increment|arithmetic circuit|alu|carry/.test(words)) return sequence(
    'Locate operands, carry/borrow input, and the function-select lines.',
    'The selected arithmetic function combines the least-significant operand bits first.',
    'Sum/difference and carry/borrow propagate through successive stages while each result bit is formed.',
    'Collect the result bits and inspect carry, overflow, sign, or zero status where shown.'
  );
  if (/decoder|encoder|multiplexer|demultiplexer|combinational/.test(words)) return sequence(
    'Separate data inputs from select, enable, and output lines.',
    'Decode the select code or evaluate the enable condition to choose one route.',
    'Only the selected gate/path propagates its input; all nonselected paths remain inactive.',
    'Read the selected output and confirm it matches the shown selection or truth-table condition.'
  );
  if (/instruction cycle|flowchart|control sequence|interrupt|fetch|decode/.test(words)) return sequence(
    'Begin at the fetch/start state and identify the instruction, flags, and external conditions.',
    'Decode the opcode and evaluate each decision diamond or timing condition.',
    'Execute the selected microoperations in arrow order, including indirect or interrupt branches when enabled.',
    'Store the result, update the program counter/state, and return to the next fetch cycle.'
  );
  if (/microprogram|control memory|microinstruction|sequenc/.test(words)) return sequence(
    'Locate the control address register, control memory, next-address inputs, and condition bits.',
    'The current address reads one microinstruction whose control field enables the required datapath operations.',
    'Branch logic combines sequencing bits and status conditions to form the next microaddress.',
    'Load the next address and repeat until the microprogram completes the machine instruction.'
  );
  if (/bus|register transfer|common bus|datapath/.test(words)) return sequence(
    'Identify source registers, destination registers, bus lines, and selection/load controls.',
    'Selection logic enables exactly one source to drive the shared bus during the control interval.',
    'The value travels across the bus while the destination load input is asserted.',
    'At the clock edge, the destination captures the value and the register-transfer operation completes.'
  );
  if (/cache|associative memory|memory hierarchy|virtual memory|page|mapping/.test(words)) return sequence(
    'Split the processor address into the tag, index/page, and offset fields shown.',
    'Use the index or associative comparison to search the relevant cache line, page entry, or memory word.',
    'On a hit, return the selected data; on a miss, follow the replacement/fetch path to the next memory level.',
    'Update tags, valid/dirty bits, or page tables as required, then deliver the requested word.'
  );
  if (/ram|rom|memory unit|memory chip|address decoding/.test(words)) return sequence(
    'Locate address inputs, chip-select, read/write controls, data lines, and storage array dimensions.',
    'The decoder activates one word line or chip corresponding to the applied address.',
    'Read mode senses the selected cells; write mode drives new bits into those cells.',
    'The selected word appears on the output lines or is retained in the addressed storage location.'
  );
  if (/pipeline|space-time|reservation table/.test(words)) return sequence(
    'Identify pipeline stages, tasks/instructions, clock intervals, and any dependency markers.',
    'The first task enters stage one; each clock advances eligible work to the next stage.',
    'Track overlapping tasks diagonally and pause where structural, data, or control hazards require a stall.',
    'After filling, the pipeline completes roughly one result per clock until it drains.'
  );
  if (/multiply|division|booth|floating.point|mantissa|exponent/.test(words)) return sequence(
    'Load operands and identify sign, exponent, fraction, quotient, divisor, or partial-product registers.',
    'Inspect the controlling bit(s) to select add, subtract, shift, normalize, or no-operation for this iteration.',
    'Update the partial result and shift the registers; repeat for the required number of operand bits.',
    'Normalize and round when needed, then combine the final sign and magnitude/fields as the result.'
  );
  if (/i\/o|input.output|dma|interrupt priority|handshak|asynchronous/.test(words)) return sequence(
    'Identify the processor, interface/controller, peripheral, data path, and request/acknowledge signals.',
    'A request establishes readiness or bus ownership; priority logic selects a requester when several compete.',
    'Data transfers while control lines provide timing, acknowledgement, direction, and completion status.',
    'Release the request/bus, update status, and notify the processor when the transfer is complete.'
  );
  if (/network|interconnection|crossbar|omega|hypercube|multiprocessor/.test(words)) return sequence(
    'Locate source processors/modules, destination modules, switches, and the available links.',
    'Destination or routing bits configure the first switch/link for the requested connection.',
    'Trace the message through successive stages; arbitration resolves any shared-link conflict.',
    'The final link reaches the destination, which accepts the data and completes the transaction.'
  );
  if (/computer|cpu|functional unit|block diagram|system/.test(words)) return sequence(
    'Identify input, memory, processor/control, arithmetic, and output blocks present in the figure.',
    'Input data and instructions enter memory; the control unit fetches and decodes the next instruction.',
    'The datapath moves operands to the ALU, performs the selected operation, and writes the result back.',
    'The completed result remains in memory/registers or travels to the output unit.'
  );
  return sequence(
    `Use the labels and caption to establish what information enters ${subject}.`,
    'Determine the role of each block or symbol and the condition that activates it.',
    'Trace every arrow from source to destination, noting intermediate transformations and feedback.',
    'Combine the final paths and labels to explain the complete result represented by the diagram.'
  );
}
