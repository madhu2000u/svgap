module grant_deadline(
    input  logic clk,
    input  logic rst_n,
    input  logic request,
    output logic grant
);

    // Internal state variables
    enum logic {IDLE, WAITING} state, next_state;
    logic request_d1; // Delayed request signal by one clock cycle

    // State transition logic
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end

    // Next state logic based on current state and inputs
    always_comb begin
        case (state)
            IDLE: 
                if (request && !request_d1)
                    next_state = WAITING;
                else
                    next_state = IDLE;
            WAITING:
                if (!request_d1)
                    next_state = IDLE;
                else
                    next_state = WAITING;
        endcase
    end

    // Delayed request signal for edge detection
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            request_d1 <= 0;
        else
            request_d1 <= request;
    end

    // Grant logic to produce a one-cycle pulse
    always_comb begin
        grant = (state == WAITING && !request_d1);
    end

endmodule
