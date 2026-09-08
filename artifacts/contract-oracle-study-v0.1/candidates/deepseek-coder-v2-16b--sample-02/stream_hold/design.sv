module stream_hold(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       s_valid,
    input  logic [7:0] s_data,
    output logic       s_ready,
    output logic       m_valid,
    output logic [7:0] m_data,
    input  logic       m_ready
);

    typedef enum {IDLE, VALID} state_t;
    state_t state, next_state;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
        end else begin
            state <= next_state;
        end
    end

    always_comb begin
        case (state)
            IDLE: begin
                s_ready = 1;
                m_valid = 0;
                m_data = 8'b0;
                if (s_valid && m_ready) begin
                    next_state = VALID;
                end else begin
                    next_state = IDLE;
                end
            end
            VALID: begin
                s_ready = 0;
                m_valid = 1;
                if (m_ready) begin
                    next_state = VALID;
                end else begin
                    next_state = VALID;
                end
                m_data = s_data;
            end
        endcase
    end

endmodule
