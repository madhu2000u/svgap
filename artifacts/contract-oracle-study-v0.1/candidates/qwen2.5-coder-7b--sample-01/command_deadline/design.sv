module command_deadline(
    input  logic clk,
    input  logic rst_n,
    input  logic start,
    output logic done
);
    logic pending;
    logic [1:0] edge_count;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pending <= 1'b0;
            edge_count <= 2'b00;
            done <= 1'b0;
        end else begin
            if (start && !pending) begin
                pending <= 1'b1;
                edge_count <= 2'b00;
            end else if (pending) begin
                if (edge_count < 3) begin
                    edge_count <= edge_count + 1;
                end else begin
                    done <= 1'b1;
                end
            end

            if (done && !start) begin
                pending <= 1'b0;
                edge_count <= 2'b00;
                done <= 1'b0;
            end
        end
    end
endmodule
